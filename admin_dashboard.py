#!/usr/bin/env python3
"""
PMD Staff Engagement Tracker — Admin Dashboard
Author: Antigravity AI
Description: A modern desktop application built with Tkinter and TTK to manage
             the PMD staff roster (staff.json), Facebook posts (posts.json),
             and trigger engagement tracking reports.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import datetime
import urllib.parse
from pathlib import Path

# Color Palette (PMD Themed)
COLOR_PRIMARY = "#1F3864"     # Dark Navy
COLOR_SECONDARY = "#2F5597"   # Royal Blue
COLOR_BG_LIGHT = "#F2F4F8"    # Soft Light Gray
COLOR_SUCCESS = "#2E7D32"     # Soft Green
COLOR_DANGER = "#C62828"      # Soft Red
COLOR_WHITE = "#FFFFFF"

class PMDAdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("PMD Staff Engagement Tracker — Admin Dashboard")
        self.root.geometry("1200x750")
        self.root.minsize(1100, 700)
        
        # Load initial data
        self.staff_file = "staff.json"
        self.posts_file = "posts.json"
        self.reports_dir = "reports"
        self.staff_list = []
        self.posts_list = []
        
        self.load_staff_data()
        self.load_posts_data()
        
        # Configure styles
        self.setup_styles()
        
        # Build UI Elements
        self.build_header()
        self.build_main_layout()
        
        # Initial loads
        self.refresh_all()

    def load_staff_data(self):
        """Loads staff roster from staff.json with error handling."""
        if not os.path.exists(self.staff_file):
            self.staff_list = []
            self.save_staff_data()
            return
            
        try:
            with open(self.staff_file, "r", encoding="utf-8") as f:
                self.staff_list = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load '{self.staff_file}': {e}")
            self.staff_list = []

    def save_staff_data(self):
        """Saves staff list to staff.json cleanly formatted."""
        try:
            with open(self.staff_file, "w", encoding="utf-8") as f:
                json.dump(self.staff_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data to '{self.staff_file}': {e}")

    def load_posts_data(self):
        """Loads posts list from posts.json with error handling."""
        if not os.path.exists(self.posts_file):
            self.posts_list = []
            self.save_posts_data()
            return
            
        try:
            with open(self.posts_file, "r", encoding="utf-8") as f:
                self.posts_list = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load '{self.posts_file}': {e}")
            self.posts_list = []

    def save_posts_data(self):
        """Saves posts list to posts.json cleanly formatted."""
        try:
            with open(self.posts_file, "w", encoding="utf-8") as f:
                json.dump(self.posts_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data to '{self.posts_file}': {e}")

    def setup_styles(self):
        """Define modern styles for TTK widgets."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Frame styles
        self.style.configure("TFrame", background=COLOR_BG_LIGHT)
        self.style.configure("Card.TFrame", background=COLOR_WHITE, relief="solid", borderwidth=1)
        
        # Label styles
        self.style.configure("TLabel", background=COLOR_BG_LIGHT, font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"), background=COLOR_BG_LIGHT, foreground=COLOR_PRIMARY)
        self.style.configure("CardHeader.TLabel", font=("Arial", 11, "bold"), background=COLOR_WHITE, foreground=COLOR_PRIMARY)
        
        # Button styles
        self.style.configure("Primary.TButton", font=("Arial", 10, "bold"))
        self.style.configure("Danger.TButton", font=("Arial", 10, "bold"))
        
        # Entry & Combobox styles
        self.style.configure("TEntry", font=("Arial", 10))
        self.style.configure("TCombobox", font=("Arial", 10))
        
        # Treeview (Table) styles
        self.style.configure("Treeview", 
            font=("Arial", 10), 
            rowheight=25, 
            background=COLOR_WHITE, 
            fieldbackground=COLOR_WHITE
        )
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background=COLOR_PRIMARY, foreground=COLOR_WHITE)
        self.style.map("Treeview.Heading", background=[("active", COLOR_SECONDARY)])
        self.style.map("Treeview", 
            background=[("selected", COLOR_PRIMARY)], 
            foreground=[("selected", COLOR_WHITE)]
        )

    def build_header(self):
        """Creates top navy blue title banner with action buttons."""
        header_frame = tk.Frame(self.root, bg=COLOR_PRIMARY, height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        left_section = tk.Frame(header_frame, bg=COLOR_PRIMARY)
        left_section.pack(side=tk.LEFT, padx=20, pady=10)
        
        title_label = tk.Label(
            left_section, 
            text="PMD Staff Engagement Tracker", 
            font=("Arial", 16, "bold"), 
            bg=COLOR_PRIMARY, 
            fg=COLOR_WHITE
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            left_section, 
            text="Admin Dashboard & Report Manager", 
            font=("Arial", 10, "italic"), 
            bg=COLOR_PRIMARY, 
            fg="#D9D9D9"
        )
        subtitle_label.pack(anchor=tk.W)
        
        # Right section with action buttons
        right_section = tk.Frame(header_frame, bg=COLOR_PRIMARY)
        right_section.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.btn_run_tracker = tk.Button(
            right_section,
            text="▶ Run Tracker Report",
            font=("Arial", 10, "bold"),
            bg=COLOR_SUCCESS,
            fg=COLOR_WHITE,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.run_tracker
        )
        self.btn_run_tracker.pack(side=tk.LEFT, padx=5)
        
        btn_overrides = tk.Button(
            right_section,
            text="⚙️ Overrides",
            font=("Arial", 10, "bold"),
            bg="#FF9800",
            fg=COLOR_WHITE,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.open_overrides_manager
        )
        btn_overrides.pack(side=tk.LEFT, padx=5)
        
        btn_refresh = tk.Button(
            right_section,
            text="🔄 Refresh",
            font=("Arial", 10, "bold"),
            bg=COLOR_SECONDARY,
            fg=COLOR_WHITE,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.refresh_all
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)

    def build_main_layout(self):
        """Sets up the left panel (staff form), center panel (staff table), right panel (posts)."""
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(container, width=280, padding=5)
        left_panel.pack(fill=tk.BOTH, side=tk.LEFT, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        center_panel = ttk.Frame(container, padding=5)
        center_panel.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=5)
        
        right_panel = ttk.Frame(container, width=300, padding=5)
        right_panel.pack(fill=tk.BOTH, side=tk.LEFT, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        self.build_add_form(left_panel)
        self.build_stats_card(left_panel)
        self.build_table_section(center_panel)
        self.build_posts_section(right_panel)

    def build_add_form(self, parent):
        """Creates the form to input a new staff member."""
        form_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        form_card.pack(fill=tk.X, pady=(0, 15))
        
        lbl_header = ttk.Label(form_card, text="➕ Add New Staff", style="CardHeader.TLabel")
        lbl_header.pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Label(form_card, text="Full Name:", background=COLOR_WHITE).pack(anchor=tk.W, pady=(5, 2))
        self.ent_name = ttk.Entry(form_card, width=30)
        self.ent_name.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_card, text="FB Display Name:", background=COLOR_WHITE).pack(anchor=tk.W, pady=(5, 2))
        self.ent_fb_name = ttk.Entry(form_card, width=30)
        self.ent_fb_name.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_card, text="Department:", background=COLOR_WHITE).pack(anchor=tk.W, pady=(5, 2))
        self.depts = [
            "Editorial", "Social Media", "Photography", 
            "Video Production", "IT & Systems", "Administration", 
            "Media Relations", "Other"
        ]
        self.cmb_dept = ttk.Combobox(form_card, values=self.depts, state="readonly", width=28)
        self.cmb_dept.set("Social Media")
        self.cmb_dept.pack(fill=tk.X, pady=(0, 15))
        
        btn_add = ttk.Button(form_card, text="Add Staff Member", style="Primary.TButton", command=self.add_staff_member)
        btn_add.pack(fill=tk.X, ipady=3)

    def build_stats_card(self, parent):
        """Creates a card showing current roster counts."""
        self.stats_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        self.stats_card.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        lbl_header = ttk.Label(self.stats_card, text="📊 Statistics", style="CardHeader.TLabel")
        lbl_header.pack(anchor=tk.W, pady=(0, 12))
        
        self.lbl_total_staff = ttk.Label(self.stats_card, text="Total Staff: --", font=("Arial", 11, "bold"), background=COLOR_WHITE, foreground=COLOR_SECONDARY)
        self.lbl_total_staff.pack(anchor=tk.W, pady=(0, 5))
        
        self.lbl_total_posts = ttk.Label(self.stats_card, text="Total Posts: --", font=("Arial", 11, "bold"), background=COLOR_WHITE, foreground=COLOR_SECONDARY)
        self.lbl_total_posts.pack(anchor=tk.W, pady=(0, 10))
        
        stats_canvas_frame = tk.Frame(self.stats_card, bg=COLOR_WHITE)
        stats_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = tk.Text(
            stats_canvas_frame, 
            wrap=tk.WORD, 
            bg=COLOR_WHITE, 
            fg="#333333", 
            font=("Arial", 8), 
            relief=tk.FLAT,
            height=20
        )
        self.stats_text.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.stats_text.config(state=tk.DISABLED)

    def build_table_section(self, parent):
        """Creates the search bar, main scrollable data table, and delete action button."""
        search_panel = ttk.Frame(parent)
        search_panel.pack(fill=tk.X, pady=(0, 10))
        
        lbl_search = ttk.Label(search_panel, text="🔍 Search:", font=("Arial", 10, "bold"))
        lbl_search.pack(side=tk.LEFT, padx=(0, 5))
        
        self.ent_search = ttk.Entry(search_panel, width=35)
        self.ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ent_search.bind("<KeyRelease>", self.on_search_keypress)
        
        btn_clear = ttk.Button(search_panel, text="Clear", command=self.clear_search, width=8)
        btn_clear.pack(side=tk.LEFT, padx=(5, 0))
        
        table_card = ttk.Frame(parent, style="Card.TFrame", padding=2)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ("name", "fb_name", "department")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="Full Name", anchor=tk.W)
        self.tree.heading("fb_name", text="Exact Facebook Name", anchor=tk.W)
        self.tree.heading("department", text="Department", anchor=tk.W)
        
        self.tree.column("name", width=200, anchor=tk.W)
        self.tree.column("fb_name", width=200, anchor=tk.W)
        self.tree.column("department", width=150, anchor=tk.W)
        
        scrollbar_y = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        action_bar = ttk.Frame(parent, padding=0)
        action_bar.pack(fill=tk.X)
        
        lbl_note = ttk.Label(action_bar, text="*All changes saved instantly", font=("Arial", 9, "italic"))
        lbl_note.pack(side=tk.LEFT)
        
        btn_delete = ttk.Button(
            action_bar, 
            text="❌ Delete Selected Staff", 
            style="Danger.TButton", 
            command=self.delete_selected_staff
        )
        btn_delete.pack(side=tk.RIGHT, ipady=2)

    def build_posts_section(self, parent):
        """Creates the posts management panel on the right."""
        posts_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        posts_card.pack(fill=tk.BOTH, expand=True)
        
        lbl_header = ttk.Label(posts_card, text="📱 Facebook Posts", style="CardHeader.TLabel")
        lbl_header.pack(anchor=tk.W, pady=(0, 10))
        
        form_frame = ttk.Frame(posts_card)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(form_frame, text="Post URL:", font=("Arial", 9), background=COLOR_WHITE).pack(anchor=tk.W, pady=(0, 2))
        self.ent_post_url = ttk.Entry(form_frame, width=35)
        self.ent_post_url.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(form_frame, text="Title (optional):", font=("Arial", 9), background=COLOR_WHITE).pack(anchor=tk.W, pady=(0, 2))
        self.ent_post_title = ttk.Entry(form_frame, width=35)
        self.ent_post_title.pack(fill=tk.X, pady=(0, 8))
        
        btn_add_post = ttk.Button(form_frame, text="➕ Add Post", style="Primary.TButton", command=self.add_post)
        btn_add_post.pack(fill=tk.X, ipady=2)
        
        ttk.Separator(posts_card, orient='horizontal').pack(fill='x', pady=8)
        
        self.tree_posts = ttk.Treeview(
            posts_card, 
            columns=("title", "post_id"), 
            show="headings", 
            selectmode="browse",
            height=20
        )
        
        self.tree_posts.heading("title", text="Post Title", anchor=tk.W)
        self.tree_posts.heading("post_id", text="Post ID", anchor=tk.W)
        
        self.tree_posts.column("title", width=180, anchor=tk.W)
        self.tree_posts.column("post_id", width=100, anchor=tk.W)
        
        scrollbar_y = ttk.Scrollbar(posts_card, orient=tk.VERTICAL, command=self.tree_posts.yview)
        self.tree_posts.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_posts.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        btn_delete_post = ttk.Button(
            posts_card,
            text="❌ Delete Post",
            style="Danger.TButton",
            command=self.delete_selected_post
        )
        btn_delete_post.pack(fill=tk.X, ipady=2)

    # ============================================================
    # Staff Management Functions
    # ============================================================
    
    def refresh_table(self, filter_query=""):
        """Populates or filters treeview table with staff list."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        query = filter_query.lower().strip()
        sorted_list = sorted(self.staff_list, key=lambda s: s.get("name", "").lower())
        
        for staff in sorted_list:
            name = staff.get("name", "")
            fb_name = staff.get("facebook_name", "")
            dept = staff.get("department", "")
            
            if not query or query in name.lower() or query in fb_name.lower() or query in dept.lower():
                self.tree.insert("", tk.END, values=(name, fb_name, dept))

    def refresh_posts_table(self):
        """Populates posts treeview table."""
        for item in self.tree_posts.get_children():
            self.tree_posts.delete(item)
        
        sorted_posts = sorted(self.posts_list, key=lambda p: p.get("title", "").lower())
        
        for post in sorted_posts:
            title = post.get("title", "Untitled")
            post_id = post.get("post_id", "N/A")
            self.tree_posts.insert("", tk.END, values=(title, post_id))

    def refresh_stats(self):
        """Calculates and renders statistics in the left panel stats card."""
        total_staff = len(self.staff_list)
        total_posts = len(self.posts_list)
        self.lbl_total_staff.config(text=f"Total Staff: {total_staff}")
        self.lbl_total_posts.config(text=f"Total Posts: {total_posts}")
        
        dept_counts = {}
        for staff in self.staff_list:
            d = staff.get("department", "Unknown")
            dept_counts[d] = dept_counts.get(d, 0) + 1
        
        stats_lines = []
        stats_lines.append("=== STAFF BY DEPT ===\n")
        for d in sorted(dept_counts.keys()):
            stats_lines.append(f"• {d}: {dept_counts[d]}")
        
        stats_lines.append("\n=== RECENT POSTS ===\n")
        recent_posts = sorted(self.posts_list, 
                             key=lambda p: p.get("date", ""), 
                             reverse=True)[:5]
        if recent_posts:
            for post in recent_posts:
                stats_lines.append(f"• {post.get('title', 'Untitled')}")
        else:
            stats_lines.append("No posts added yet.")
        
        stats_display_str = "\n".join(stats_lines)
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, stats_display_str)
        self.stats_text.config(state=tk.DISABLED)

    def refresh_all(self):
        """Refresh all UI elements: staff table, posts table, and stats."""
        self.refresh_table()
        self.refresh_posts_table()
        self.refresh_stats()

    def add_staff_member(self):
        """Form submission logic to insert a new staff member."""
        name = self.ent_name.get().strip()
        fb_name = self.ent_fb_name.get().strip()
        dept = self.cmb_dept.get()
        
        if not name:
            messagebox.showwarning("Validation Error", "Full Name is required!")
            self.ent_name.focus()
            return
            
        if not fb_name:
            messagebox.showwarning("Validation Error", "Facebook Display Name is required!")
            self.ent_fb_name.focus()
            return
        
        for staff in self.staff_list:
            if staff.get("facebook_name", "").lower() == fb_name.lower():
                messagebox.showerror("Duplicate Record", f"Facebook name '{fb_name}' already exists!")
                return
        
        new_staff = {
            "name": name,
            "facebook_name": fb_name,
            "department": dept
        }
        
        self.staff_list.append(new_staff)
        self.save_staff_data()
        
        self.ent_name.delete(0, tk.END)
        self.ent_fb_name.delete(0, tk.END)
        self.cmb_dept.set("Social Media")
        
        self.ent_search.delete(0, tk.END)
        self.refresh_all()
        
        messagebox.showinfo("Success", f"Added '{name}' to roster!")

    def delete_selected_staff(self):
        """Deletes selected staff member in treeview table."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Select a staff member to delete.")
            return
        
        values = self.tree.item(selected_item, "values")
        name = values[0]
        fb_name = values[1]
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Delete '{name}'?")
        
        if confirm:
            self.staff_list = [s for s in self.staff_list if s.get("facebook_name") != fb_name]
            self.save_staff_data()
            self.refresh_all()
            messagebox.showinfo("Deleted", f"'{name}' removed from roster.")

    # ============================================================
    # Posts Management Functions
    # ============================================================
    
    def add_post(self):
        """Parse Facebook URL, extract IDs, and append to posts.json."""
        url = self.ent_post_url.get().strip()
        if not url:
            messagebox.showwarning("Validation Error", "Post URL is required!")
            return
        
        title = self.ent_post_title.get().strip() or "Untitled Post"
        
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        post_id = None
        page_id = None
        
        if "fbid" in query:
            post_id = query["fbid"][0]
            if "set" in query:
                set_val = query["set"][0]
                if "." in set_val:
                    page_id = set_val.split(".")[1]
                else:
                    page_id = set_val
        elif "story_fbid" in query and "id" in query:
            post_id = query["story_fbid"][0]
            page_id = query["id"][0]
        
        if not post_id:
            path_parts = [p for p in parsed.path.split('/') if p]
            if "posts" in path_parts:
                idx = path_parts.index("posts")
                if idx + 1 < len(path_parts):
                    post_id = path_parts[idx + 1]
                    if idx > 0:
                        possible_page = path_parts[idx - 1]
                        if possible_page.isdigit():
                            page_id = possible_page
        
        if not post_id or not page_id:
            messagebox.showerror("Parse Error", "Could not extract IDs from URL.\nEnsure it's a valid Facebook post link.")
            return
        
        combined_id = f"{page_id}_{post_id}"
        
        for p in self.posts_list:
            if p.get("post_id") == combined_id:
                messagebox.showwarning("Duplicate", "This post is already added.")
                return
        
        new_post = {
            "post_id": combined_id,
            "title": title,
            "link": url,
            "date": datetime.date.today().isoformat()
        }
        
        self.posts_list.append(new_post)
        self.save_posts_data()
        
        self.ent_post_url.delete(0, tk.END)
        self.ent_post_title.delete(0, tk.END)
        self.refresh_all()
        
        messagebox.showinfo("Success", f"Post added!\nID: {combined_id}")

    def delete_selected_post(self):
        """Deletes selected post from posts.json."""
        selected_item = self.tree_posts.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Select a post to delete.")
            return
        
        values = self.tree_posts.item(selected_item, "values")
        title = values[0]
        post_id = values[1]
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Delete '{title}'?")
        
        if confirm:
            self.posts_list = [p for p in self.posts_list if p.get("post_id") != post_id]
            self.save_posts_data()
            self.refresh_all()
            messagebox.showinfo("Deleted", f"'{title}' removed.")

    # ============================================================
    # Tracker Execution
    # ============================================================
    
    def run_tracker(self):
        """Executes tracker.py and shows the result."""
        if not self.staff_list:
            messagebox.showwarning("No Data", "Add staff members before running tracker.")
            return
        
        if not self.posts_list:
            messagebox.showwarning("No Data", "Add Facebook posts before running tracker.")
            return
        
        try:
            self.btn_run_tracker.config(state=tk.DISABLED, text="⏳ Running...")
            self.root.update()
            
            result = subprocess.run(
                ["python3", "tracker.py"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            self.btn_run_tracker.config(state=tk.NORMAL, text="▶ Run Tracker Report")
            
            if result.returncode == 0:
                report_file = self.get_latest_report()
                if report_file:
                    messagebox.showinfo(
                        "Success",
                        f"Report generated!\n\n{report_file}\n\nCheck reports folder for details."
                    )
                else:
                    messagebox.showinfo("Success", "Tracker executed!\nCheck reports folder.")
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                messagebox.showerror("Execution Error", f"Tracker failed:\n\n{error_msg[:500]}")
        
        except subprocess.TimeoutExpired:
            self.btn_run_tracker.config(state=tk.NORMAL, text="▶ Run Tracker Report")
            messagebox.showerror("Timeout", "Tracker execution timed out after 2 minutes.")
        except Exception as e:
            self.btn_run_tracker.config(state=tk.NORMAL, text="▶ Run Tracker Report")
            messagebox.showerror("Error", f"Failed to run tracker:\n{e}")

    def get_latest_report(self):
        """Returns the latest report file name, if it exists."""
        if not os.path.exists(self.reports_dir):
            return None
        
        report_files = [
            f for f in os.listdir(self.reports_dir)
            if f.endswith(".xlsx") and f.startswith("PMD_Engagement_Report_")
        ]
        
        if report_files:
            report_files.sort(reverse=True)
            return report_files[0]
        
        return None

    # ============================================================
    # UI Event Handlers
    # ============================================================
    
    def on_search_keypress(self, event):
        """Real-time filter as the user types in the search box."""
        query = self.ent_search.get()
        self.refresh_table(query)

    def clear_search(self):
        """Clears search box and resets table filters."""
        self.ent_search.delete(0, tk.END)
        self.refresh_table()

    def open_overrides_manager(self):
        """Opens a modal window to manage manual engagement overrides."""
        overrides_window = tk.Toplevel(self.root)
        overrides_window.title("Manage Engagement Overrides")
        overrides_window.geometry("700x500")
        
        # Instructions
        lbl_info = tk.Label(
            overrides_window,
            text="Mark staff as reacted/commented when API fails to detect them.\nOverrides are saved in overrides.json and applied during tracker runs.",
            font=("Arial", 10),
            wraplength=650,
            justify=tk.LEFT
        )
        lbl_info.pack(fill=tk.X, padx=15, pady=10)
        
        # Main form frame
        form_frame = ttk.Frame(overrides_window, padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Post ID:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ent_post_id = ttk.Combobox(form_frame, values=[p.get("post_id") for p in self.posts_list], width=40)
        ent_post_id.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(form_frame, text="Staff Name:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        ent_staff_name = ttk.Combobox(form_frame, values=[s.get("name") for s in self.staff_list], width=30)
        ent_staff_name.grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(form_frame, text="Action:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        var_action = tk.StringVar(value="reacted")
        ttk.Radiobutton(form_frame, text="Reacted", variable=var_action, value="reacted").grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Radiobutton(form_frame, text="Commented", variable=var_action, value="commented").grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        
        def add_override():
            post_id = ent_post_id.get().strip()
            staff_name = ent_staff_name.get().strip()
            action = var_action.get()
            
            if not post_id or not staff_name:
                messagebox.showwarning("Input Required", "Select both post and staff member.")
                return
            
            # Load current overrides
            overrides_path = 'overrides.json'
            overrides = {}
            if os.path.exists(overrides_path):
                try:
                    with open(overrides_path, 'r', encoding='utf-8') as f:
                        overrides = json.load(f)
                except Exception:
                    overrides = {}
            
            # Add override
            if post_id not in overrides:
                overrides[post_id] = {}
            
            if action == "reacted":
                overrides[post_id][staff_name] = {"reacted": True, "reaction": "LIKE"}
            else:
                overrides[post_id][staff_name] = {"commented": True}
            
            # Save
            try:
                with open(overrides_path, 'w', encoding='utf-8') as f:
                    json.dump(overrides, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Override added for {staff_name} on post {post_id[:20]}...")
                refresh_overrides_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save override: {e}")
        
        btn_add = ttk.Button(form_frame, text="➕ Add Override", command=add_override)
        btn_add.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=10, ipady=3)
        
        # Overrides list
        ttk.Separator(overrides_window, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
        ttk.Label(overrides_window, text="Current Overrides:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=15, pady=(5, 5))
        
        tree_overrides = ttk.Treeview(overrides_window, columns=("post", "staff", "action"), show="headings", height=15)
        tree_overrides.heading("post", text="Post ID", anchor=tk.W)
        tree_overrides.heading("staff", text="Staff Name", anchor=tk.W)
        tree_overrides.heading("action", text="Action", anchor=tk.W)
        
        tree_overrides.column("post", width=200, anchor=tk.W)
        tree_overrides.column("staff", width=200, anchor=tk.W)
        tree_overrides.column("action", width=100, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(overrides_window, orient=tk.VERTICAL, command=tree_overrides.yview)
        tree_overrides.configure(yscrollcommand=scrollbar.set)
        
        tree_overrides.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=10, pady=5)
        scrollbar.pack(fill=tk.Y, side=tk.LEFT, pady=5)
        
        def refresh_overrides_list():
            for item in tree_overrides.get_children():
                tree_overrides.delete(item)
            
            overrides_path = 'overrides.json'
            if os.path.exists(overrides_path):
                try:
                    with open(overrides_path, 'r', encoding='utf-8') as f:
                        overrides = json.load(f)
                    for post_id, staff_dict in overrides.items():
                        for staff_name, override_data in staff_dict.items():
                            action = "Reacted" if override_data.get('reacted') else "Commented"
                            tree_overrides.insert("", tk.END, values=(post_id[:25], staff_name, action))
                except Exception:
                    pass
        
        def delete_override():
            selected = tree_overrides.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Select an override to delete.")
                return
            
            values = tree_overrides.item(selected, "values")
            post_id = values[0]
            staff_name = values[1]
            
            overrides_path = 'overrides.json'
            if os.path.exists(overrides_path):
                try:
                    with open(overrides_path, 'r', encoding='utf-8') as f:
                        overrides = json.load(f)
                    
                    # Find full post id
                    for full_post_id in list(overrides.keys()):
                        if full_post_id.startswith(post_id[:25]):
                            if staff_name in overrides[full_post_id]:
                                del overrides[full_post_id][staff_name]
                                if not overrides[full_post_id]:
                                    del overrides[full_post_id]
                    
                    with open(overrides_path, 'w', encoding='utf-8') as f:
                        json.dump(overrides, f, indent=2, ensure_ascii=False)
                    messagebox.showinfo("Deleted", "Override removed.")
                    refresh_overrides_list()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete: {e}")
        
        btn_delete = ttk.Button(overrides_window, text="❌ Delete Selected Override", command=delete_override)
        btn_delete.pack(fill=tk.X, padx=10, pady=5, ipady=2)
        
        refresh_overrides_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = PMDAdminDashboard(root)
    root.mainloop()
