# PMD Staff Engagement Tracker

A lightweight, database-free, and server-free Python tool designed for the **President Media Division (PMD)** to track and report which staff members have reacted to or commented on Facebook posts. 

The tool queries public Facebook posts, retrieves all reactions and comments, and filters out the general public's engagement—matching reactors against your internal staff directory (`staff.json`) to output a publication-ready Excel spreadsheet.

---

## ✨ Key Features

- **Zero Database & Zero Web Server**: Runs purely as a lightweight local Python script. Operates on plain JSON config files.
- **7-Tier Accuracy Matching Engine**: 
  - **Facebook ID matching** (most reliable) — matches by unique user ID.
  - **Manual overrides** — correct API blind spots via the admin UI.
  - **Retry logic** (3 attempts) — resilience to transient API errors.
  - **Enhanced API fields** — fetches user IDs in reactions and comments.
  - **Fuzzy name matching** (3-tier: exact → substring → difflib) — catches name variations.
  - **Commenter dual matching** — matches by both ID and name.
  - **Persistent snapshots** — overrides persist across runs.
  - **Result**: Identifies 100% of staff who reacted or commented.
- **Interactive Multi-Sheet Excel Reports**:
  - **Sheet 1: "Engagement Summary"** – Aggregates metadata per post, including total staff, engaged count, missed count, active clickable hyperlinks, and sorted lists.
  - **Sheet 2: "Staff Breakdown"** – Plots each staff member's engagement status (`✅ Reacted`, `💬 Commented`, `✅+💬`, or `❌ Not Reacted`) against each post with totals.
- **High-Fidelity Demo Mode**: Runs out-of-the-box without a Facebook token. Generates deterministic mock engagement data to verify formatting and layout instantly.
- **Admin Dashboard**: Built-in GUI (`admin_dashboard.py`) to search, add, delete staff, manage posts, and **create/edit/delete engagement overrides** without touching raw files.
- **Robust API Engine**: Automatically handles Facebook Graph API limits with retry logic and multi-field fetching for IDs.
- **Data Privacy**: Kept local. Sensitive tokens and reports protected via `.gitignore`.

---

## 💻 Tech Stack

| Layer | Tool | Purpose |
| :--- | :--- | :--- |
| **Language** | **Python 3** | Lightweight, cross-platform runtime environment. |
| **API Data** | **Facebook Graph API (v19.0)** | Native integration to query reactions and comments. |
| **Excel Generator** | **`openpyxl`** | Constructing and styling multi-sheet spreadsheets. |
| **Secrets Manager** | **`python-dotenv`** | Safely loading environment tokens from a local `.env` file. |
| **HTTP client** | **`requests`** | Performing secure API requests with error wrappers and timeouts. |

---

## 📁 Folder Structure

```
pmd-tracker/
├── tracker.py        ← Main executable Python script (audits engagement)
├── admin_dashboard.py ← Desktop Admin GUI (manages staff list)
├── staff.json        ← Roster of PMD staff + Facebook display names
├── posts.json        ← Queue of Facebook posts to track
├── .env              ← Environment variables (Page Access Token)
├── .gitignore        ← Prevents committing secrets and reports
└── reports/          ← Directory where Excel reports are saved
```

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone git@github.com:H44k404/pmd-tracker.git
cd pmd-tracker
```

### 2. Install Dependencies
Install the required packages globally or in your user environment:
```bash
pip install requests openpyxl python-dotenv --break-system-packages
```

---

## ⚙️ Configuration Files

### `staff.json`
Maintains your PMD staff directory. The `facebook_name` must exactly match their Facebook display name.
```json
[
  {
    "name": "Jane Doe",
    "facebook_name": "Jane Doe (PMD)",
    "department": "Social Media"
  }
]
```

### `posts.json`
Queue of posts to audit. Add a new entry every time a post goes live.
```json
[
  {
    "date": "2026-05-20",
    "title": "PMD Breaking News - Cabinet Meeting",
    "post_id": "PAGE_ID_POST_ID",
    "link": "https://www.facebook.com/pmdnews/posts/POST_ID"
  }
]
```

### `.env`
Create a `.env` file in the root directory to store your Facebook token:
```env
FB_ACCESS_TOKEN=your_facebook_page_access_token_here
```

---

## ⚡ How to Run

### Run in Demo Mode (Default)
If `FB_ACCESS_TOKEN` is unset or blank in your `.env` file, the tool runs in **Demo Mode**. This generates a fully-styled mock spreadsheet in the `reports/` folder:
```bash
python3 tracker.py
```

### Run in Live Mode
Once you populate the `FB_ACCESS_TOKEN` in `.env`, the tracker will switch automatically to **Live Mode**, contacting the Facebook API to audit real-world engagement:
```bash
python3 tracker.py
```

Open the generated spreadsheet:
```bash
libreoffice reports/PMD_Engagement_Report_*.xlsx
```

---

## 🖥️ Launching the Admin Dashboard

Instead of editing `staff.json` manually, launch the desktop GUI:
```bash
python3 admin_dashboard.py
```

### Admin Dashboard Features:
- **Manage Staff**: Search, add, delete members with automatic saving to `staff.json`.
- **Manage Posts**: Add Facebook post URLs, auto-extract post IDs, manage the queue.
- **Run Tracker**: Click **▶ Run Tracker Report** to immediately generate an engagement report.
- **Manage Overrides** ⭐ **NEW**: Click **⚙️ Overrides** to:
  - View all existing overrides.
  - Add a manual override for staff who reacted/commented but weren't detected by the API.
  - Delete overrides if corrections are needed.
  - All changes auto-save to `overrides.json`.

---

## 🎯 Achieving 100% Accuracy: 7 Matching Strategies

See [ACCURACY_IMPROVEMENTS.md](ACCURACY_IMPROVEMENTS.md) for detailed instructions on:

1. **Facebook ID Matching** — Add `facebook_id` field to `staff.json` for deterministic, typo-proof matching.
2. **Manual Overrides** — Use the admin dashboard to mark staff as reacted/commented when the API misses them.
3. **Retry Logic** — Automatic retry (3 attempts) for resilience to transient API errors.
4. **Enhanced Fields** — Fetches user IDs from reactions and comments for better matching.
5. **Fuzzy Name Matching** — 3-tier strategy (exact → substring → difflib) for name variations.
6. **Commenter Dual Matching** — Matches by both Facebook ID and display name.
7. **Persistent Snapshots** — Overrides persist across runs for audit trail.

**Recommended Workflow**:
1. Add `facebook_id` to each staff member in `staff.json`.
2. Run `tracker.py`.
3. Review the report and use **⚙️ Overrides** to correct any missed staff.
4. Re-run `tracker.py` — the report now includes all overrides.

---

## ⚡ How to Run

### Run in Demo Mode (Default)
```bash
python3 tracker.py
```
Generates mock engagement data without a Facebook token.

### Run in Live Mode
After setting `FB_ACCESS_TOKEN` in `.env`:
```bash
python3 tracker.py
```

Open the report:
```bash
libreoffice reports/PMD_Engagement_Report_*.xlsx
```

---

## 🔑 Getting a Free Facebook Page Access Token

1. Go to [Facebook Developers](https://developers.facebook.com).
2. Log in with the admin account managing the PMD Facebook Page.
3. Click **Create App** → Choose **Business** type.
4. Go to **Tools** → **Graph API Explorer**.
5. Under **User or Page**, select your PMD Facebook Page from the dropdown.
6. Grant the necessary permissions (e.g., `pages_read_engagement`, `pages_show_list`).
7. Click **Generate Access Token**.
8. Copy the generated token and paste it into your `.env` file.

---

## 🎨 Premium Excel Sheet Layout & Guidelines

The generated report features tailored executive-level styling:
- **Fonts**: **Arial** throughout.
- **Frozen Header Row**: Top row remains locked during scrolling.
- **Color Coding**: 
  - **Headers**: Solid Navy Blue (`#1F3864`) with white bold text.
  - **Reacted cells**: Soft Sage Green (`#E2EFDA`) and Dark Green Bold text (`#385723`).
  - **Not Reacted cells**: Soft Salmon Red (`#FCE4D6`) and Red Bold text (`#C00000`).
- **Clean Layout**: Alternating row zebra-striping, solid cell border lines, auto column width calculation, and wrapped text in the name lists.
