# PMD Staff Engagement Tracker

A lightweight, database-free, and server-free Python tool designed for the **President Media Division (PMD)** to track and report which staff members have reacted to or commented on Facebook posts. 

The tool queries public Facebook posts, retrieves all reactions and comments, and filters out the general public's engagement—matching reactors against your internal staff directory (`staff.json`) to output a publication-ready Excel spreadsheet.

---

## ✨ Key Features

- **Zero Database & Zero Web Server**: Runs purely as a lightweight local Python script. Operates on plain JSON config files.
- **Double-Verification Matching Engine**: Matches the exact Facebook display name from a roster (`staff.json`) against reactors and commentators to verify engagement.
- **Interactive Multi-Sheet Excel Reports**:
  - **Sheet 1: "Engagement Summary"** – Aggregates metadata per post, including total staff, engaged count, missed count, active clickable hyperlinks, and wrapped, sorted lists of names.
  - **Sheet 2: "Staff Breakdown"** – Plots each staff member's engagement status (`✅ Reacted` or `❌ Not Reacted`) against each post with total engagement tallies.
- **High-Fidelity Demo Mode**: Runs out-of-the-box without a Facebook token. Generates deterministic mock engagement data seeded with `42` to verify formatting and layout instantly.
- **Robust API Engine**: Automatically handles Facebook Graph API limit restrictions and cursor-based pagination (`paging.next`) to scale seamlessly.
- **Data Privacy**: Kept local. Sensitive environment tokens and generated reports are protected from leaks using `.gitignore`.

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
├── tracker.py        ← Main executable Python script
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
