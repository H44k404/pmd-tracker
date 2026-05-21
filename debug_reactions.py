#!/usr/bin/env python3
"""
Debug script: prints the EXACT names returned by Facebook Graph API for a post.
Run: python3 debug_reactions.py
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("FB_ACCESS_TOKEN", "").strip()

if not token:
    print("❌ No FB_ACCESS_TOKEN found in .env")
    exit(1)

# Load posts.json to list available posts
with open("posts.json", "r") as f:
    posts = json.load(f)

print("Available posts:")
for i, p in enumerate(posts):
    print(f"  [{i}] {p['title']} — ID: {p['post_id']}")

print()
# Debug each post
for post in posts:
    post_id = post["post_id"]
    print(f"━━━ {post['title']} ({post_id}) ━━━")
    url = f"https://graph.facebook.com/v19.0/{post_id}/reactions"
    params = {"fields": "name,type", "access_token": token, "limit": 500}
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        if "error" in data:
            print(f"  ❌ API Error: {data['error'].get('message')}")
        else:
            reactors = data.get("data", [])
            if not reactors:
                print("  (no reactions)")
            for r in reactors:
                print(f"  ✅ name='{r.get('name')}' | type={r.get('type')}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    print()
