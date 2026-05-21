# PMD Engagement Tracker — User Guide & Report

This document explains what the PMD Engagement Tracker does, how it works, and how to use the tool. It's written for non-technical users and contains practical steps and troubleshooting tips.

**What this tool does:**
- Reads a list of staff and Facebook posts from `staff.json` and `posts.json`.
- For each post, it fetches reactions and comments from Facebook using the Facebook Graph API.
- Matches staff members to people who reacted or commented and generates a structured Excel report (`reports/PMD_Engagement_Report_YYYY-MM-DD.xlsx`).

**Why use it:**
- Quickly see which staff reacted (Liked, Loved, etc.) or commented on specific posts.
- Produce a shareable Excel summary and a per-staff breakdown for follow-up.

Overview (non-technical)
- You give the tool: a list of staff and the posts you care about.
- The tool asks Facebook (using a secure token you provide) who reacted or commented on those posts.
- It compares the names returned by Facebook to the names in your staff list, using a smart matching algorithm to tolerate small differences in spelling.
- It produces an Excel file with two sheets: `Engagement Summary` and `Staff Breakdown`.

Key files
- `staff.json` — staff entries (name, department, and `facebook_name`). Add `facebook_id` if you want more precise matching.
- `posts.json` — list of posts to check. `post_id` must be in the format `<PAGEID>_<POSTID>`.
- `.env` — contains `FB_ACCESS_TOKEN`. Keep this private. Example: `FB_ACCESS_TOKEN=EAA...`
- `reports/PMD_Engagement_Report_YYYY-MM-DD.xlsx` — generated report.

How to run (copy-paste)
1. Ensure `FB_ACCESS_TOKEN` in `.env` is a valid Page Access Token.
2. Run the tracker:
```
python3 tracker.py
```
3. Open the generated Excel file in the `reports` folder.

Admin GUI
- Run `python3 admin_dashboard.py` to launch a Tkinter-based admin interface for managing staff and posts and for running the tracker from a simple GUI.

What the report shows (explain columns)
- Engagement Summary (sheet):
  - Date, Post Title, Post Link — identifying info.
  - Total Staff — number of staff rows in `staff.json`.
  - ✅ Reacted — how many staff were detected reacting to the post.
  - ❌ Not Reacted — staff not detected as reacting.
  - Reaction Details — which staff reacted and with which reaction (Like, Care, etc.).
  - Who Reacted — list of staff display names that reacted.
  - Who Commented — list of commenter names detected on the post.
  - Who Did NOT React — list of staff who did not react.

- Staff Breakdown (sheet):
  - One row per staff member. Each post column shows status per post: `✅ Reacted`, `💬 Commented`, `✅+💬` (both), or `❌ Not Reacted`.

Matching algorithm (brief)
- The tool attempts to match staff names to Facebook names using the following order:
  1. Exact normalized match (case and whitespace normalized).
 2. Substring containment (either direction).
 3. Fuzzy similarity using Python's `difflib` SequenceMatcher (default threshold ~0.75).
- For the most reliable results, add `facebook_id` to `staff.json` and the tool will match by ID.

Permissions & tokens (important)
- To read page reactions/comments you need a Page Access Token that has `pages_read_engagement` and `pages_show_list` permissions.
- If you have only a user token, run `/me/accounts` to get Page tokens for pages you manage.
- If the app is in Development mode, only app admins/testers can grant permissions — other accounts will not work until App Review approves scopes.

Limitations & notes
- Facebook privacy can prevent some reactions/comments from being returned by the API — a user may appear in the UI but not in the API.
- Reactions/comments can appear with slightly different display names; fuzzy-matching helps but is not perfect.
- Some posts or reactions can return an "Unsupported get request" if the post ID is incorrect or the token does not have access to that post.

Troubleshooting
- If the tracker falls back to DEMO MODE:
  - Check `.env` and ensure `FB_ACCESS_TOKEN` is a valid Page Access Token (no quotes/newlines).
  - Test with cURL: `curl -s "https://graph.facebook.com/v25.0/me?access_token=YOUR_TOKEN"`
- If `/me/accounts` returns an error:
  - Ensure the token belongs to an admin of the page, and the requested scopes are granted.
- If staff are not matched:
  - Try adding `facebook_id` in `staff.json` for deterministic matching, or adjust `facebook_name` to exactly match the account display names.

Security & privacy
- Keep `.env` and any tokens private. Do NOT commit secrets to public repositories (the repository was updated on request — make sure tokens are not pushed).

Future improvements
- Add `facebook_id` support in the UI and matching by ID.
- Add scheduled runs and a small web UI for better reporting.

Contact / Next steps
- If you want, I can implement `facebook_id`-based matching, add a manual override UI, or schedule automated runs. Tell me which option you prefer.

---
Generated: 2026-05-21
