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
import time
import datetime
import requests
from dotenv import load_dotenv

# Openpyxl for styled Excel report generation
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load environment variables
load_dotenv()

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

def get_facebook_reactions(post_id, access_token):
    """
    Fetches all reactors' names on a post using Facebook Graph API.
    Handles pagination. Returns a set of reactor names.
    """
    reactors = set()
    url = f"https://graph.facebook.com/v19.0/{post_id}/reactions"
    params = {
        "fields": "name,id",
        "access_token": access_token,
        "limit": 500
    }
    
    while url:
        try:
            # For the first call, we pass params. For subsequent paginated calls, 
            # url already contains access_token and query parameters.
            response = requests.get(
                url, 
                params=params if url.endswith("/reactions") else None, 
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                print(f"\n  ❌ Facebook Graph API Error (Reactions for post {post_id}): {error_msg}")
                return None
                
            data = response.json()
            for item in data.get("data", []):
                # Skip reaction silently if name is missing
                name = item.get("name")
                if name:
                    reactors.add(name)
                    
            # Get next page URL
            url = data.get("paging", {}).get("next")
            params = None
            
        except Exception as e:
            print(f"\n  ❌ Exception while fetching reactions for post {post_id}: {e}")
            return None
            
    return reactors

def get_facebook_comments(post_id, access_token):
    """
    Fetches all commentators' names on a post using Facebook Graph API.
    Handles pagination. Returns a set of commentator names.
    """
    commentators = set()
    url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
    params = {
        "fields": "from{name}",
        "access_token": access_token,
        "limit": 500
    }
    
    while url:
        try:
            response = requests.get(
                url, 
                params=params if url.endswith("/comments") else None, 
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                print(f"\n  ❌ Facebook Graph API Error (Comments for post {post_id}): {error_msg}")
                return None
                
            data = response.json()
            for item in data.get("data", []):
                # Extract 'from.name' safely, skip silently if missing
                from_user = item.get("from")
                if from_user:
                    name = from_user.get("name")
                    if name:
                        commentators.add(name)
                        
            # Get next page URL
            url = data.get("paging", {}).get("next")
            params = None
            
        except Exception as e:
            print(f"\n  ❌ Exception while fetching comments for post {post_id}: {e}")
            return None
            
    return commentators

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
        "✅ Reacted", "❌ Not Reacted", "Who Reacted", "Who Did NOT React"
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
        c_date = ws_summary.cell(row=row_idx, column=1, value=post["date"])
        c_date.alignment = align_center
        
        # Title
        c_title = ws_summary.cell(row=row_idx, column=2, value=post["title"])
        c_title.alignment = align_left
        
        # Link
        c_link = ws_summary.cell(row=row_idx, column=3, value=post["link"])
        c_link.hyperlink = post["link"]
        c_link.font = link_font
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
        
        # Who Reacted (Comma-separated)
        who_reacted_str = ", ".join(engaged_names)
        c_who_r = ws_summary.cell(row=row_idx, column=7, value=who_reacted_str)
        c_who_r.alignment = align_left
        
        # Who Did NOT React (Comma-separated)
        who_not_reacted_str = ", ".join(missed_names)
        c_who_nr = ws_summary.cell(row=row_idx, column=8, value=who_not_reacted_str)
        c_who_nr.alignment = align_left
        
        # Set shared properties per cell in the row
        for col_idx in range(1, 9):
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
        # Cap "Who Reacted" and "Who Did NOT React" to prevent insanely wide columns
        if col_letter in ["G", "H"]:
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
            
            # Check if this staff member is in the engaged set
            is_engaged = fb_name in post_eng.get("fb_engaged_set", set())
            
            col_pos = 3 + post_idx
            status_text = "✅ Reacted" if is_engaged else "❌ Not Reacted"
            cell = ws_breakdown.cell(row=row_idx, column=col_pos, value=status_text)
            cell.alignment = align_center
            cell.border = thin_border
            
            if is_engaged:
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
    fb_token = os.getenv("FB_ACCESS_TOKEN")
    is_demo = False
    
    if not fb_token or fb_token.strip() == "" or fb_token == "your_facebook_page_access_token_here":
        is_demo = True
        print("⚠️  Running in DEMO MODE — add FB token to .env for live data\n")
        # Initialize seed for reproducible demo generation
        random.seed(42)
    
    engagement_data = {}
    
    for i, post in enumerate(posts_list):
        post_title = post["title"]
        post_id = post["post_id"]
        print(f"  📡  Fetching: {post_title}")
        
        if is_demo:
            # Simulate slight processing delay for a premium interactive feel
            time.sleep(0.4)
            
            # Seed-reproducible random staff engagement selection
            # We vary engagement rates per post to make data realistic and dynamic
            rates = [0.28, 0.19, 0.36, 0.22, 0.31]
            rate = rates[i % len(rates)]
            
            # Select random subset of staff who engaged
            engaged_staff = []
            missed_staff = []
            fb_engaged_set = set()
            
            for staff in staff_list:
                # We determine if staff engaged.
                # In demo mode, a person is engaged if they reacted OR commented.
                # We draw a single random threshold for engagement.
                if random.random() < rate:
                    engaged_staff.append(staff["name"])
                    fb_engaged_set.add(staff["facebook_name"])
                else:
                    missed_staff.append(staff["name"])
                    
            # Sort lists alphabetically for a clean premium presentation
            engaged_staff.sort()
            missed_staff.sort()
            
            engagement_data[post_id] = {
                "engaged_names": engaged_staff,
                "missed_names": missed_staff,
                "fb_engaged_set": fb_engaged_set
            }
            
        else:
            # Live mode using Facebook Graph API
            reactors = get_facebook_reactions(post_id, fb_token)
            comments = get_facebook_comments(post_id, fb_token)
            
            # If either API call failed completely (returned None), skip post
            if reactors is None or comments is None:
                print(f"  ⚠️  Skipping post '{post_title}' due to fetching error.")
                continue
                
            # Union of both names to get total engaged facebook names
            live_engaged_fb_names = reactors.union(comments)
            
            engaged_staff = []
            missed_staff = []
            fb_engaged_set = set()
            
            # Filter and match staff
            for staff in staff_list:
                fb_name = staff["facebook_name"]
                if fb_name in live_engaged_fb_names:
                    engaged_staff.append(staff["name"])
                    fb_engaged_set.add(fb_name)
                else:
                    missed_staff.append(staff["name"])
                    
            engaged_staff.sort()
            missed_staff.sort()
            
            engagement_data[post_id] = {
                "engaged_names": engaged_staff,
                "missed_names": missed_staff,
                "fb_engaged_set": fb_engaged_set
            }
            
    # Generate the highly styled Excel report
    try:
        report_path = generate_report(staff_list, posts_list, engagement_data, is_demo)
        print()
        print(f"✅  Report saved → {report_path}")
    except Exception as e:
        print(f"\n❌ Error generating Excel report: {e}")

if __name__ == "__main__":
    run()
