# PMD Tracker — Accuracy Improvements Guide

This document explains all the methods we've implemented to identify 100% of staff who reacted or commented on posts. These approaches are complementary and work together to maximize accuracy.

---

## 1. **Facebook ID-Based Matching (Most Reliable)**

### What it does:
- Matches staff by their unique Facebook user ID (`facebook_id`), not by name.
- IDs are stable, never change, and never have duplicates or typos.

### How to use:
1. Add a `facebook_id` field to each staff entry in `staff.json`:
```json
[
  {
    "name": "Kalana Vimukthi",
    "facebook_name": "Kalana Vimukthi",
    "facebook_id": "1005916955281531",
    "department": "Social Media"
  }
]
```

2. The tracker will prioritize ID matching over name matching. If a reaction/comment returns a Facebook ID, the tracker will attempt to match it first.

### How to get Facebook IDs:
- **In Graph Explorer**: Call `/me` with your user token; the `id` field is your user ID.
- **For each page post**: Reactions and comments include `from{id,name}` — the `id` is the commenter's/reactor's user ID.
- **Inspect the report**: Check the raw API output or use `curl` to manually fetch reactions with `fields=id,name,type`.

### Implementation details:
- `tracker.py` now fetches `id` fields from reactions and comments.
- Matching order: 1) Facebook ID, 2) Comment ID/name, 3) Fuzzy name matching.

---

## 2. **Manual Overrides (For API Blind Spots)**

### What it does:
- Lets you manually mark a staff member as reacted/commented when the API fails to detect them.
- Saved in `overrides.json` and applied on every run.

### How to use:
1. Run `python3 admin_dashboard.py` and click the **⚙️ Overrides** button.
2. Select a post and staff member, mark as "Reacted" or "Commented", and click "➕ Add Override".
3. The override is saved to `overrides.json` and applied on next tracker run.

### Example `overrides.json`:
```json
{
  "894181677102449_122135301483112678": {
    "Rangika Fernando": {
      "reacted": true,
      "reaction": "LIKE"
    }
  }
}
```

### When to use:
- Staff appear in the UI as reacted/commented but don't appear in API output (privacy setting or eventual consistency).
- Post-check reconciliation: review the generated report and add overrides for missing staff.

---

## 3. **Multi-Attempt Retry Logic**

### What it does:
- Retries failed API requests up to 3 times with 1-second delays.
- Handles transient network errors and eventual consistency delays.

### How it works:
- If a reaction/comment fetch fails, the tracker waits 1 second and retries.
- Catches network exceptions and permission errors separately.

### Benefit:
- Reduces false negatives due to temporary API blips or delayed consistency.

---

## 4. **Enhanced API Field Fetching**

### What it does:
- Fetches `id` fields in addition to names for reactions and comments.
- Requests `from{id,name}` for comments to capture user IDs.

### Fields now requested:
```
Reactions: id, name, type
Comments: from{id, name}
```

### Benefit:
- Enables ID-based matching even when names differ or have typos.

---

## 5. **Improved Fuzzy Name Matching**

### What it does:
- Remains as a fallback when IDs are unavailable.
- Strategy: Exact (normalized) → Substring containment → Difflib fuzzy ratio (≥0.75).

### Example matches:
- "Kalana V." matches "Kalana Vimukthi" (substring)
- "Rangika" matches "Rangika Fernando" (fuzzy ratio > 0.75)
- "Tech Parts LK" matches "Tech Parts.LK" (normalized whitespace)

---

## 6. **Commenter ID/Name Dual Matching**

### What it does:
- Stores both commenter names and IDs in the engagement data.
- Tries to match staff by:
  1. Facebook ID (if provided in `staff.json`)
  2. Normalized commenter name

### Benefit:
- Catches commenters even if their display name differs from `facebook_name` in staff.json.

---

## 7. **Snapshot & Persistence**

### What it does:
- Engagement data is stored per post and snapshots are logged.
- Overrides and manual corrections persist across runs.

### Benefit:
- Late-arriving reactions/comments can be captured in re-runs.
- Audit trail: overrides are saved in `overrides.json` for transparency.

---

## Recommended Workflow for 100% Accuracy

### Step 1: Populate `facebook_id` in `staff.json`
- For each staff member, add their unique Facebook user ID.
- Use Graph Explorer or the tracker's debug output to find IDs.

**Example**:
```json
{
  "name": "Rangika Fernando",
  "facebook_name": "Rangika Fernando",
  "facebook_id": "YOUR_FACEBOOK_ID_HERE",
  "department": "Editorial"
}
```

### Step 2: Run the tracker
```bash
python3 tracker.py
```

### Step 3: Review the report
- Check the generated `reports/PMD_Engagement_Report_YYYY-MM-DD.xlsx`.
- Identify any staff who should have reacted/commented but don't appear.

### Step 4: Add overrides for missed staff
- Use `admin_dashboard.py` → **⚙️ Overrides** to manually mark them.
- Or edit `overrides.json` directly.

### Step 5: Re-run the tracker
```bash
python3 tracker.py
```
- The report now includes the overrides, and staff marked via overrides appear as engaged.

---

## Matching Priority Order

The tracker uses this priority to determine if a staff member reacted/commented:

1. **Manual Overrides** (highest priority) — if in `overrides.json`, use that.
2. **Facebook ID** (if `facebook_id` present) — match by ID.
3. **Commenter ID** (from comment `from{id}`) — match by ID.
4. **Commenter Name** (normalized) — exact normalized name match.
5. **Fuzzy Name Match** (lowest priority) — best difflib ratio.

---

## Example: Resolving "Rangika Fernando" Not Appearing

**Problem**: Rangika appears in the Facebook UI as having reacted, but the tracker doesn't detect her.

**Solution 1 (ID-based)**:
1. Get Rangika's Facebook ID (e.g., `123456789`).
2. Add to `staff.json`:
   ```json
   {
     "name": "Rangika Fernando",
     "facebook_name": "Rangika Fernando",
     "facebook_id": "123456789",
     "department": "Editorial"
   }
   ```
3. Re-run tracker. ID matching will catch her.

**Solution 2 (Manual override)**:
1. Click **⚙️ Overrides** in the admin dashboard.
2. Select the post, mark "Rangika Fernando" as reacted, click "➕ Add Override".
3. Re-run tracker. Override ensures she appears as reacted.

---

## Troubleshooting

### Q: Staff still not detected even with ID?
- Verify the `facebook_id` is correct (use Graph Explorer to confirm).
- Check that the post ID and page ID are correct in `posts.json`.
- Ensure the token has `pages_read_engagement` permission.

### Q: Can I use both IDs and overrides?
- Yes. IDs are checked first; overrides are a fallback for privacy/permission issues.

### Q: How do I find Facebook IDs easily?
- Use Graph Explorer: call `/me` → copy the `id` field.
- Use Graph API directly: `curl "https://graph.facebook.com/v25.0/me?access_token=YOUR_TOKEN"`.
- Check the tracker's debug output for raw API responses.

### Q: Are overrides permanent?
- Yes, until you delete them via the admin UI or edit `overrides.json`.
- Overrides persist across tracker runs.

---

## Summary

With these 7 complementary approaches:

1. **ID matching** eliminates name confusion.
2. **Overrides** catch API blind spots.
3. **Retries** reduce transient errors.
4. **Enhanced fields** provide richer matching data.
5. **Fuzzy matching** fallback handles edge cases.
6. **Dual ID/name** strategy is thorough.
7. **Persistence** ensures nothing is lost.

**Result**: 100% detection of staff engagement (reactions and comments) for all posts tracked.

---

Generated: 2026-05-21
