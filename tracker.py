#!/usr/bin/env python3
"""
PMD Staff Engagement Tracker
Author: Antigravity AI
Description: A lightweight Python tool for the President Media Division (PMD)
             that tracks which staff members reacted to or commented on Facebook posts.
"""

import os
import json
import random
import re
import time
import datetime
import requests
import difflib
from dotenv import load_dotenv

# Openpyxl for styled Excel report generation
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load environment variables
load_dotenv()


def validate_facebook_token(access_token):
    """Validate the provided Facebook access token.
    Returns a dict with keys:
      - ok: bool
      - error: optional error message
      - data: optional dict with 'me' and 'pages' information
    """
    if not access_token:
        return {"ok": False, "error": "No access token provided"}

    base = "https://graph.facebook.com/v25.0"
    try:
        # Basic token test: /me
        r_me = requests.get(f"{base}/me", params={"access_token": access_token}, timeout=15)
        if r_me.status_code != 200:
            try:
                err = r_me.json().get("error", {}).get("message", r_me.text)
            except Exception:
                err = r_me.text
            return {"ok": False, "error": f"/me failed: {err}"}

        me = r_me.json()

        # Try /me/accounts to see if this user token can list pages (and obtain page tokens)
        r_pages = requests.get(f"{base}/me/accounts", params={"access_token": access_token}, timeout=15)
        pages = []
        if r_pages.status_code == 200:
            pages = r_pages.json().get("data", [])
        else:
            # If pages endpoint fails, capture message but still return user info
            try:
                pages_err = r_pages.json().get("error", {}).get("message", r_pages.text)
            except Exception:
                pages_err = r_pages.text
            pages = {"error": pages_err}

        return {"ok": True, "data": {"me": me, "pages": pages}}

    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": f"Request failed: {e}"}


def print_header():
    print("=======================================================")
    print("       PMD Staff Engagement Tracker")
    print("=======================================================")

def load_json_files():
    """Load staff.json and posts.json with clear error reporting."""
    staff_path = "staff.json"
    posts_path = "posts.json"

    if not os.path.exists(staff_path):
        print(f"❌ Error: Missing file '{staff_path}' in the current directory.")
        print("Please ensure 'staff.json' is present. Refer to build instructions for the schema.")
        return None, None

    if not os.path.exists(posts_path):
        print(f"❌ Error: Missing file '{posts_path}' in the current directory.")
        print("Please ensure 'posts.json' is present. Refer to build instructions for the schema.")
        return None, None

    try:
        with open(staff_path, "r", encoding="utf-8") as f:
            staff_list = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: 'staff.json' contains invalid JSON syntax: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error loading 'staff.json': {e}")
        return None, None

    try:
        with open(posts_path, "r", encoding="utf-8") as f:
            posts_list = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: 'posts.json' contains invalid JSON syntax: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error loading 'posts.json': {e}")
        return None, None

    return staff_list, posts_list

def normalize_name(value):
    """Normalize Facebook names for consistent matching."""
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value.strip().lower())


def find_best_reactor_match(fb_name, reactors, min_ratio=0.75):
    """Find best matching reactor key for a staff facebook name.
    reactors: dict mapping normalized_name -> {original, type}
    Returns the reactor key (normalized) if a match is found, else None.
    Matching strategy:
      1. Exact normalized match
      2. Substring containment (either direction)
      3. Fuzzy ratio (difflib.SequenceMatcher) >= min_ratio
    """
    if not fb_name or not reactors:
        return None

    target = normalize_name(fb_name)
    # exact
    if target in reactors:
        return target

    keys = list(reactors.keys())

    # substring matches
    for k in keys:
        if target in k or k in target:
            return k

    # fuzzy matching
    best_key = None
    best_ratio = 0.0
    for k in keys:
        ratio = difflib.SequenceMatcher(None, target, k).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_key = k

    if best_ratio >= min_ratio:
        return best_key

    return None


def get_facebook_reactions(post_id, access_token):
    """
    Fetches all reactors' names and their reaction types on a post using Facebook Graph API.
    Returns a dict mapping normalized Facebook name -> (original_name, reaction_type), or
    an auth error object with {'auth_error': True, 'message': ...} when the token is invalid.
    """
    reactors = {}  # key: normalized name, value: (original_name, reaction_type)
    url = f"https://graph.facebook.com/v19.0/{post_id}/reactions"
    params = {
        "fields": "id,name,type",
        "access_token": access_token,
        "limit": 500
    }
    attempts = 0
    while url:
        attempts += 1
        try:
            response = requests.get(url, params=params if url.endswith("/reactions") else None, timeout=30)
            if response.status_code != 200:
                error_data = response.json().get("error", {})
                error_msg = error_data.get("message", "Unknown error")
                error_code = error_data.get("code")
                print(f"\n  ❌  Facebook Graph API Error (Reactions for post {post_id}): {error_msg}")
                if error_code == 190 or "access token" in error_msg.lower():
                    return {"auth_error": True, "message": error_msg}
                if "unsupported get request" in error_msg.lower() or "missing permissions" in error_msg.lower():
                    return {"unsupported_error": True, "message": error_msg}
                return None
            data = response.json()
            for item in data.get("data", []):
                name = item.get("name", "")
                r_type = item.get("type") or "UNKNOWN"
                rid = item.get("id")
                if name:
                    # Store with normalized key for case-insensitive matching
                    reactors[normalize_name(name)] = {"original": name, "type": r_type, "id": rid}
            url = data.get("paging", {}).get("next")
            params = None
        except Exception as e:
            print(f"\n  ❌  Exception while fetching reactions for post {post_id}: {e}")
            # retry a couple times
            if attempts < 3:
                time.sleep(1)
                continue
            return None
    print(f"    ℹ️  Total reactors found: {len(reactors)}")
    return reactors


def get_facebook_comments(post_id, access_token):
    """
    Fetches all commentators' names on a post using Facebook Graph API.
    Handles pagination. Returns a set of commentator names.
    """
    commentators = set()
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
    params = {
        "fields": "from{id,name}",
        "access_token": access_token,
        "limit": 500
    }
    attempts = 0

    while url:
        attempts += 1
        try:
            response = requests.get(
                url, 
                params=params if url.endswith("/comments") else None, 
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                print(f"\n  ❌ Facebook Graph API Error (Comments for post {post_id}): {error_msg}")
                if attempts < 3:
                    time.sleep(1)
                    continue
                return None
                
            data = response.json()
            for item in data.get("data", []):
                # Extract 'from.name' safely, skip silently if missing
                from_user = item.get("from")
                if from_user:
                    name = from_user.get("name")
                    if name:
                        commentators.add(name)
                    # also handle id if available via extended matching
                    uid = from_user.get('id')
                    if uid:
                        commentators.add(str(uid))
                        
            # Get next page URL
            url = data.get("paging", {}).get("next")
            params = None
            
        except Exception as e:
            print(f"\n  ❌ Exception while fetching comments for post {post_id}: {e}")
            if attempts < 3:
                time.sleep(1)
                continue
            return None
            
    return commentators

def build_demo_engagement(staff_list, posts_list):
    """Generate a reproducible demo engagement data set for all posts."""
    random.seed(42)
    rates = [0.28, 0.19, 0.36, 0.22, 0.31]
    possible_reacts = ["LIKE", "LOVE", "CARE", "HAHA", "WOW", "SAD", "ANGRY"]
    engagement_data = {}

    for i, post in enumerate(posts_list):
        rate = rates[i % len(rates)]
        engaged_staff = []
        missed_staff = []
        fb_engaged_set = set()
        reactions_map = {}

        for staff in staff_list:
            fb_name = staff["facebook_name"]
            if random.random() < rate:
                engaged_staff.append(staff["name"])
                fb_engaged_set.add(fb_name)
                reactions_map[fb_name] = random.choice(possible_reacts)
            else:
                missed_staff.append(staff["name"])

        engaged_staff.sort()
        missed_staff.sort()

        engagement_data[post["post_id"]] = {
            "engaged_names": engaged_staff,
            "missed_names": missed_staff,
            "fb_engaged_set": fb_engaged_set,
            "reactions": reactions_map,
            "commenters_set": set(),
            "commenters": []
        }

    return engagement_data

def generate_report(staff_list, posts_list, engagement_data, is_demo):
    """
    Generates a premium, highly formatted Excel workbook using openpyxl.
    """
    wb = openpyxl.Workbook()
    
    # ----------------------------------------------------
    # Styles Definition
    # ----------------------------------------------------
    font_family = "Arial"
    
    # Fonts
    title_font = Font(name=font_family, size=16, bold=True, color="1F3864")
    header_font = Font(name=font_family, size=11, bold=True, color="FFFFFF")
    data_font = Font(name=font_family, size=10)
    bold_data_font = Font(name=font_family, size=10, bold=True)
    link_font = Font(name=font_family, size=10, color="0563C1", underline="single")
    
    reacted_font = Font(name=font_family, size=10, bold=True, color="385723")
    not_reacted_font = Font(name=font_family, size=10, bold=True, color="C00000")
    
    # Fills
    header_fill = PatternFill(start_color="1F3864", end_color="1F3864", fill_type="solid")
    alt_row_fill = PatternFill(start_color="F2F4F8", end_color="F2F4F8", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    
    reacted_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    not_reacted_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    
    # Borders & Alignments
    thin_side = Side(style='thin', color='D9D9D9')
    thin_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    
    # ----------------------------------------------------
    # Sheet 1: Engagement Summary
    # ----------------------------------------------------
    ws_summary = wb.active
    ws_summary.title = "Engagement Summary"
    ws_summary.views.sheetView[0].showGridLines = True
    
    # Header columns
    summary_headers = [
        "Date", "Post Title", "Post Link", "Total Staff", 
        "✅ Reacted", "❌ Not Reacted", "Reaction Details", "Who Reacted", "Who Commented", "Who Did NOT React"
    ]
    
    # Set header row height
    ws_summary.row_dimensions[1].height = 26
    
    # Write and style headers
    for col_idx, header in enumerate(summary_headers, 1):
        cell = ws_summary.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = thin_border
        
    # Write data rows
    for row_idx, post in enumerate(posts_list, 2):
        post_id = post["post_id"]
        post_eng = engagement_data.get(post_id, {})
        
        engaged_names = post_eng.get("engaged_names", [])
        missed_names = post_eng.get("missed_names", [])
        
        engaged_count = len(engaged_names)
        missed_count = len(missed_names)
        
        # Decide fill based on zebra striping
        row_fill = alt_row_fill if row_idx % 2 == 0 else white_fill
        
        # Date
        c_date = ws_summary.cell(row=row_idx, column=1, value=post.get("date", datetime.date.today().isoformat()))
        c_date.alignment = align_center
        
        # Title
        c_title = ws_summary.cell(row=row_idx, column=2, value=post["title"])
        c_title.alignment = align_left
        
        # Link
        c_link = ws_summary.cell(row=row_idx, column=3, value=post.get("link", ""))
        if post.get("link"):
            c_link.hyperlink = post["link"]
            c_link.font = link_font
        else:
            c_link.font = data_font
        c_link.alignment = align_left
        
        # Total Staff
        c_total = ws_summary.cell(row=row_idx, column=4, value=len(staff_list))
        c_total.alignment = align_center
        
        # ✅ Reacted (use soft green highlight for data cell to pop)
        c_reacted = ws_summary.cell(row=row_idx, column=5, value=engaged_count)
        c_reacted.font = reacted_font
        c_reacted.fill = reacted_fill
        c_reacted.alignment = align_center
        
        # ❌ Not Reacted (use soft red highlight)
        c_not_reacted = ws_summary.cell(row=row_idx, column=6, value=missed_count)
        c_not_reacted.font = not_reacted_font
        c_not_reacted.fill = not_reacted_fill
        c_not_reacted.alignment = align_center

        # Reaction Details (name:reaction)
        reactions_map = post_eng.get("reactions", {})
        reaction_details = []
        for staff in staff_list:
            fb_name = staff.get("facebook_name")
            if fb_name in reactions_map:
                reaction = reactions_map[fb_name]
                reaction_details.append(f"{staff.get('name')} ({reaction})")
        reaction_details_str = ", ".join(reaction_details)
        c_reaction_details = ws_summary.cell(row=row_idx, column=7, value=reaction_details_str)
        c_reaction_details.alignment = align_left
        
        # Who Reacted (Comma-separated)
        who_reacted_str = ", ".join(engaged_names)
        c_who_r = ws_summary.cell(row=row_idx, column=8, value=who_reacted_str)
        c_who_r.alignment = align_left

        # Who Commented (Comma-separated)
        commenters = post_eng.get("commenters_set", set())
        commenters_list = sorted(list(commenters)) if commenters else []
        who_commented_str = ", ".join(commenters_list)
        c_who_c = ws_summary.cell(row=row_idx, column=9, value=who_commented_str)
        c_who_c.alignment = align_left

        # Who Did NOT React (Comma-separated)
        who_not_reacted_str = ", ".join(missed_names)
        c_who_nr = ws_summary.cell(row=row_idx, column=10, value=who_not_reacted_str)
        c_who_nr.alignment = align_left
        
        # Set shared properties per cell in the row
        for col_idx in range(1, 10):
            cell = ws_summary.cell(row=row_idx, column=col_idx)
            cell.border = thin_border
            if col_idx not in [5, 6]:  # Don't overwrite the specialized green/red fills
                cell.fill = row_fill
            if col_idx not in [3, 5, 6]:  # Don't overwrite specialized link/color fonts
                cell.font = data_font
                
    # Freeze header row on Sheet 1
    ws_summary.freeze_panes = "A2"
    
    # Adjust column widths dynamically for Sheet 1
    for col in ws_summary.columns:
        col_letter = col[0].column_letter
        max_len = 0
        for cell in col:
            if cell.value:
                val_str = str(cell.value)
                # Split by newline to check max line length
                for line in val_str.split("\n"):
                    if len(line) > max_len:
                        max_len = len(line)
        # Give safety padding
        width = max(max_len + 3, 12)
        # Cap "Reaction Details", "Who Reacted" and "Who Did NOT React" to prevent insanely wide columns
        if col_letter in ["G", "H", "I"]:
            width = 45
        elif col_letter == "B": # Title column
            width = min(width, 40)
        elif col_letter == "C": # Link column
            width = min(width, 35)
        ws_summary.column_dimensions[col_letter].width = width

    # ----------------------------------------------------
    # Sheet 2: Staff Breakdown
    # ----------------------------------------------------
    ws_breakdown = wb.create_sheet(title="Staff Breakdown")
    ws_breakdown.views.sheetView[0].showGridLines = True
    
    # Header columns: Staff Name, Department, [Post Titles], Total Engaged, Total Missed
    breakdown_headers = ["Staff Name", "Department"]
    for post in posts_list:
        breakdown_headers.append(post["title"])
    breakdown_headers.extend(["Total Engaged", "Total Missed"])
    
    # Set header row height
    ws_breakdown.row_dimensions[1].height = 26
    
    # Write and style headers
    for col_idx, header in enumerate(breakdown_headers, 1):
        cell = ws_breakdown.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = thin_border
        
    # Write data rows (one per staff member)
    num_posts = len(posts_list)
    for row_idx, staff in enumerate(staff_list, 2):
        staff_name = staff["name"]
        fb_name = staff["facebook_name"]
        dept = staff["department"]
        
        # Count individual stats
        total_engaged = 0
        total_missed = 0
        
        # Zebra striping fill for baseline cells
        row_fill = alt_row_fill if row_idx % 2 == 0 else white_fill
        ws_breakdown.row_dimensions[row_idx].height = 20
        
        # Staff Name
        c_name = ws_breakdown.cell(row=row_idx, column=1, value=staff_name)
        c_name.font = data_font
        c_name.fill = row_fill
        c_name.alignment = align_left
        c_name.border = thin_border
        
        # Department
        c_dept = ws_breakdown.cell(row=row_idx, column=2, value=dept)
        c_dept.font = data_font
        c_dept.fill = row_fill
        c_dept.alignment = align_left
        c_dept.border = thin_border
        
        # Post columns
        for post_idx, post in enumerate(posts_list):
            post_id = post["post_id"]
            post_eng = engagement_data.get(post_id, {})
            
            # Check engagement by reactions and comments
            engaged = fb_name in post_eng.get("fb_engaged_set", set())
            commented = normalize_name(fb_name) in post_eng.get("commenters_set", set())

            col_pos = 3 + post_idx
            if engaged and commented:
                status_text = "✅+💬"
            elif engaged:
                status_text = "✅ Reacted"
            elif commented:
                status_text = "💬 Commented"
            else:
                status_text = "❌ Not Reacted"
            cell = ws_breakdown.cell(row=row_idx, column=col_pos, value=status_text)
            cell.alignment = align_center
            cell.border = thin_border
            
            if engaged or commented:
                cell.font = reacted_font
                cell.fill = reacted_fill
                total_engaged += 1
            else:
                cell.font = not_reacted_font
                cell.fill = not_reacted_fill
                total_missed += 1
                
        # Total Engaged
        c_tot_eng = ws_breakdown.cell(row=row_idx, column=3 + num_posts, value=total_engaged)
        c_tot_eng.font = bold_data_font
        c_tot_eng.fill = row_fill
        c_tot_eng.alignment = align_center
        c_tot_eng.border = thin_border
        
        # Total Missed
        c_tot_mis = ws_breakdown.cell(row=row_idx, column=4 + num_posts, value=total_missed)
        c_tot_mis.font = bold_data_font
        c_tot_mis.fill = row_fill
        c_tot_mis.alignment = align_center
        c_tot_mis.border = thin_border
        
    # Freeze header row on Sheet 2
    ws_breakdown.freeze_panes = "A2"
    
    # Adjust column widths dynamically for Sheet 2
    for col in ws_breakdown.columns:
        col_letter = col[0].column_letter
        max_len = 0
        for cell in col:
            if cell.value:
                val_str = str(cell.value)
                for line in val_str.split("\n"):
                    if len(line) > max_len:
                        max_len = len(line)
        width = max(max_len + 3, 12)
        # Cap post titles columns to keep them reasonable
        col_idx = col[0].column
        if 3 <= col_idx < 3 + num_posts:
            width = min(width, 22)
        ws_breakdown.column_dimensions[col_letter].width = width

    # Save to report directory
    os.makedirs("reports", exist_ok=True)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    report_filename = f"reports/PMD_Engagement_Report_{today_str}.xlsx"
    wb.save(report_filename)
    return report_filename

def run():
    print_header()
    
    staff_list, posts_list = load_json_files()
    if staff_list is None or posts_list is None:
        return
        
    print(f"  👥  Staff loaded : {len(staff_list)}")
    print(f"  📄  Posts loaded : {len(posts_list)}")
    print()
    
    # Detect mode
    fb_token = os.getenv("FB_ACCESS_TOKEN", "")
    fb_token = fb_token.strip()
    is_demo = False
    
    if not fb_token or fb_token == "your_facebook_page_access_token_here":
        is_demo = True
        print("⚠️  Running in DEMO MODE — add FB token to .env for live data\n")

    if not is_demo:
        print("🔎 Validating Facebook access token...")
        tv = validate_facebook_token(fb_token)
        if not tv.get("ok"):
            print(f"\n🚫 Facebook token validation failed: {tv.get('error')}")
            print("   Switching to DEMO MODE — ensure FB_ACCESS_TOKEN is a valid Page Access Token with pages_read_engagement/pages_show_list scopes.\n")
            is_demo = True
        else:
            me = tv.get("data", {}).get("me", {})
            pages = tv.get("data", {}).get("pages", [])
            print(f"  ✅ Token valid for user: {me.get('name', '(unknown)')} (id: {me.get('id', '')})")
            if isinstance(pages, list):
                if len(pages) == 0:
                    print("  ⚠️  No pages available from this token. To fetch Page reactions, obtain a Page Access Token via /me/accounts.")
                    is_demo = True
                else:
                    print(f"  📄 {len(pages)} page(s) accessible. Prefer using a Page Access Token for live fetches.")
            else:
                # pages may be an error dict. This commonly happens when the provided token
                # is already a Page Access Token (pages cannot be listed from a page token).
                if isinstance(pages, dict) and pages.get('error'):
                    # If the token's /me id matches one of the page ids in posts.json,
                    # treat this as a valid Page Access Token and continue with live fetches.
                    try:
                        post_page_ids = {str(p.split('_', 1)[0]) for p in [pp.get('post_id','') for pp in load_json_files()[1]] if p}
                    except Exception:
                        post_page_ids = set()
                    me_id = str(me.get('id', ''))
                    if me_id and me_id in post_page_ids:
                        print(f"  ✅ Token appears to be a Page Access Token for page id {me_id}; proceeding with live fetches.")
                    else:
                        print(f"  ⚠️  Could not list pages: {pages.get('error')}")
                        is_demo = True
    
    # Load manual overrides if present
    overrides = {}
    overrides_path = 'overrides.json'
    if os.path.exists(overrides_path):
        try:
            with open(overrides_path, 'r', encoding='utf-8') as f:
                overrides = json.load(f)
        except Exception:
            overrides = {}

    engagement_data = {}
    live_fetch_failures = 0

    if is_demo:
        engagement_data = build_demo_engagement(staff_list, posts_list)
    else:
        for post in posts_list:
            post_title = post["title"]
            post_id = post["post_id"]
            print(f"  📡  Fetching: {post_title}")
            # fetch reactors and commenters with retries and snapshot
            reactors = get_facebook_reactions(post_id, fb_token)
            if reactors is None:
                print(f"  ⚠️  Skipping post '{post_title}' due to fetching error.")
                live_fetch_failures += 1
                continue
            if reactors.get("auth_error"):
                print("\n🚫 Facebook access token invalid or expired.")
                print("   Update .env with a fresh FB_ACCESS_TOKEN and rerun the tracker.")
                return
            if reactors.get("unsupported_error"):
                print("\n🚫 Facebook Graph API unsupported request or missing permissions detected.")
                print("   Confirm the token belongs to the page that owns these posts and has pages_read_engagement/pages_show_list.")
                live_fetch_failures += 1
                continue

            engaged_staff = []
            missed_staff = []
            fb_engaged_set = set()
            reactions_map = {}

            # fetch commenters and normalized commenter set
            commenters = set()
            commenters_id_set = set()
            if 'commenters' in post.get('post_id', ''):
                pass
            comments_raw = get_facebook_comments(post_id, fb_token)
            if isinstance(comments_raw, set):
                for c in comments_raw:
                    # comments_raw may contain names and ids (ids are numeric strings)
                    if c and c.isdigit():
                        commenters_id_set.add(c)
                    elif c:
                        commenters.add(c)
            # normalized commenters set for matching
            commenters_norm_set = {normalize_name(n) for n in commenters}

            # Determine reaction engagement based on reactors dict keys (normalized lowercase)
            for staff in staff_list:
                fb_name = staff["facebook_name"].strip()
                staff_fb_id = str(staff.get('facebook_id')) if staff.get('facebook_id') else None

                # 1) check manual overrides for this post
                over = overrides.get(post_id, {}).get(staff.get('name'))
                if over:
                    # apply override flags
                    if over.get('reacted'):
                        engaged_staff.append(staff['name'])
                        fb_engaged_set.add(staff.get('facebook_name'))
                        reactions_map[staff.get('facebook_name')] = over.get('reaction','(override)')
                        continue
                    if over.get('commented'):
                        # mark as commented (counted as engaged)
                        missed_staff.append(staff['name'])
                        # we'll reflect in commenters set below
                        continue

                # 2) match by facebook_id if provided
                matched = False
                if staff_fb_id:
                    # reactors may include id values in their dicts
                    for rnorm, rdata in reactors.items():
                        if rdata.get('id') and str(rdata.get('id')) == staff_fb_id:
                            engaged_staff.append(staff['name'])
                            fb_engaged_set.add(staff.get('facebook_name'))
                            reactions_map[staff.get('facebook_name')] = rdata.get('type')
                            matched = True
                            break
                    if matched:
                        continue

                # 3) match by commenters id/name
                if staff_fb_id and staff_fb_id in commenters_id_set:
                    engaged_staff.append(staff['name'])
                    fb_engaged_set.add(staff.get('facebook_name'))
                    matched = True
                    continue

                if normalize_name(fb_name) in commenters_norm_set:
                    engaged_staff.append(staff['name'])
                    fb_engaged_set.add(staff.get('facebook_name'))
                    matched = True
                    continue

                # 4) match by reactors name using fuzzy matching
                matched_key = find_best_reactor_match(fb_name, reactors)
                if matched_key:
                    engaged_staff.append(staff["name"])  # display name
                    fb_engaged_set.add(staff.get("facebook_name"))
                    reactions_map[staff.get("facebook_name")] = reactors[matched_key]["type"]
                    if normalize_name(staff.get("facebook_name")) != matched_key:
                        print(f"    🔎 Fuzzy matched '{staff.get('facebook_name')}' -> '{reactors[matched_key]['original']}' (ratio/substring)")
                else:
                    missed_staff.append(staff["name"])  # name for display
                    # print no-match only for debugging
                    print(f"    ⚠️  No match for staff: '{fb_name}'")

            engaged_staff.sort()
            missed_staff.sort()

            engagement_data[post_id] = {
                "engaged_names": engaged_staff,
                "missed_names": missed_staff,
                "fb_engaged_set": fb_engaged_set,
                "reactions": reactions_map,
                "commenters": sorted(list(commenters)),
                "commenters_set": commenters_norm_set
            }
            # attempt to fetch commenters for the post
            comments = get_facebook_comments(post_id, fb_token)
            if comments is None:
                commenters_list = []
                commenters_set_norm = set()
            else:
                commenters_list = sorted(list(comments))
                commenters_set_norm = {normalize_name(n) for n in comments}

            engagement_data[post_id]["commenters"] = commenters_list
            engagement_data[post_id]["commenters_set"] = commenters_set_norm

        if live_fetch_failures == len(posts_list):
            print("\n⚠️  All live fetches failed due to unsupported request or missing permissions.")
            print("   Switching to DEMO MODE to generate a placeholder report.")
            is_demo = True
            engagement_data = build_demo_engagement(staff_list, posts_list)
            
    # Generate the highly styled Excel report
    try:
        report_path = generate_report(staff_list, posts_list, engagement_data, is_demo)
        print()
        print(f"✅  Report saved → {report_path}")
    except Exception as e:
        print(f"\n❌ Error generating Excel report: {e}")

if __name__ == "__main__":
    run()
