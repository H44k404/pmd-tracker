#!/usr/bin/env python3
"""
PMD Staff Engagement Tracker — Admin Dashboard
Author: Antigravity AI
Description: A modern desktop application built with Tkinter and TTK to manage
             the PMD staff roster (staff.json) without manually editing JSON files.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

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
        self.root.title("PMD Staff Roster Manager")
        self.root.geometry("950x650")
        self.root.minsize(900, 600)
        
        # Load initial data
        self.staff_file = "staff.json"
        self.staff_list = []
        self.load_staff_data()
        
        # Configure styles
        self.setup_styles()
        
        # Build UI Elements
        self.build_header()
        self.build_main_layout()
        
        # Initial table load
        self.refresh_table()

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
        self.style.configure("Stat.TLabel", font=("Arial", 10, "bold"), background=COLOR_WHITE)
        
        # Button styles
        self.style.configure("Primary.TButton", font=("Arial", 10, "bold"), background=COLOR_PRIMARY, foreground=COLOR_WHITE)
        self.style.map("Primary.TButton", background=[("active", COLOR_SECONDARY)])
        
        self.style.configure("Danger.TButton", font=("Arial", 10, "bold"), background=COLOR_DANGER, foreground=COLOR_WHITE)
        self.style.map("Danger.TButton", background=[("active", "#B71C1C")])
        
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
        
        # Selected row color
        self.style.map("Treeview", 
            background=[("selected", COLOR_PRIMARY)], 
            foreground=[("selected", COLOR_WHITE)]
        )

    def load_staff_data(self):
        """Loads staff roster from staff.json with error handling."""
        if not os.path.exists(self.staff_file):
            # Create a blank staff list if file doesn't exist
            self.staff_list = []
            self.save_staff_data()
            return
            
        try:
            with open(self.staff_file, "r", encoding="utf-8") as f:
                self.staff_list = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load '{self.staff_file}': {e}\nInitializing clean roster list.")
            self.staff_list = []

    def save_staff_data(self):
        """Saves staff list to staff.json cleanly formatted."""
        try:
            with open(self.staff_file, "w", encoding="utf-8") as f:
                json.dump(self.staff_list, f, indent=2, ensure_ascii=False)
            self.refresh_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data to '{self.staff_file}': {e}")

    def build_header(self):
        """Creates top navy blue title banner."""
        header_frame = tk.Frame(self.root, bg=COLOR_PRIMARY, height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="PMD Staff Roster Manager", 
            font=("Arial", 16, "bold"), 
            bg=COLOR_PRIMARY, 
            fg=COLOR_WHITE
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Super Admin Dashboard", 
            font=("Arial", 10, "italic"), 
            bg=COLOR_PRIMARY, 
            fg="#D9D9D9"
        )
        subtitle_label.pack(side=tk.LEFT, pady=16)

    def build_main_layout(self):
        """Sets up the left panel (inputs) and right panel (table)."""
        # Outer container frame with padding
        container = ttk.Frame(self.root, padding=15)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel (Add Form + Stats)
        left_panel = ttk.Frame(container, width=320, padding=5)
        left_panel.pack(fill=tk.BOTH, side=tk.LEFT, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right Panel (Search, Table, Actions)
        right_panel = ttk.Frame(container, padding=5)
        right_panel.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        self.build_add_form(left_panel)
        self.build_stats_card(left_panel)
        self.build_table_section(right_panel)

    def build_add_form(self, parent):
        """Creates the form to input a new staff member."""
        form_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        form_card.pack(fill=tk.X, pady=(0, 15))
        
        # Header
        lbl_header = ttk.Label(form_card, text="➕ Add New Staff Member", style="CardHeader.TLabel")
        lbl_header.pack(anchor=tk.W, pady=(0, 15))
        
        # Full Name
        ttk.Label(form_card, text="Full Name:", background=COLOR_WHITE).pack(anchor=tk.W, pady=(5, 2))
        self.ent_name = ttk.Entry(form_card, width=30)
        self.ent_name.pack(fill=tk.X, pady=(0, 10))
        
        # Facebook Name
        ttk.Label(form_card, text="Facebook Display Name:", background=COLOR_WHITE).pack(anchor=tk.W, pady=(5, 2))
        self.ent_fb_name = ttk.Entry(form_card, width=30)
        self.ent_fb_name.pack(fill=tk.X, pady=(0, 10))
        
        # Department Dropdown
        ttk.Label(form_card, text="Department:", background=COLOR_WHITE).pack(anchor=tk.W, pady=(5, 2))
        self.depts = [
            "Editorial", "Social Media", "Photography", 
            "Video Production", "IT & Systems", "Administration", 
            "Media Relations", "Other"
        ]
        self.cmb_dept = ttk.Combobox(form_card, values=self.depts, state="readonly", width=28)
        self.cmb_dept.set("Social Media")
        self.cmb_dept.pack(fill=tk.X, pady=(0, 15))
        
        # Add Button
        btn_add = ttk.Button(form_card, text="Add Staff Member", style="Primary.TButton", command=self.add_staff_member)
        btn_add.pack(fill=tk.X, ipady=3)

    def build_stats_card(self, parent):
        """Creates a card showing current roster counts."""
        self.stats_card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        self.stats_card.pack(fill=tk.BOTH, expand=True)
        
        lbl_header = ttk.Label(self.stats_card, text="📊 Live Roster Statistics", style="CardHeader.TLabel")
        lbl_header.pack(anchor=tk.W, pady=(0, 12))
        
        # Total Staff Count
        self.lbl_total_staff = ttk.Label(self.stats_card, text="Total Staff: --", font=("Arial", 11, "bold"), background=COLOR_WHITE, foreground=COLOR_SECONDARY)
        self.lbl_total_staff.pack(anchor=tk.W, pady=(0, 10))
        
        # Scrollable stats box
        stats_canvas_frame = tk.Frame(self.stats_card, bg=COLOR_WHITE)
        stats_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = tk.Text(
            stats_canvas_frame, 
            wrap=tk.WORD, 
            bg=COLOR_WHITE, 
            fg="#333333", 
            font=("Arial", 9), 
            relief=tk.FLAT,
            height=12
        )
        self.stats_text.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        
        # Disabled text box
        self.stats_text.config(state=tk.DISABLED)
        
        # Populate initial stats
        self.refresh_stats()

    def build_table_section(self, parent):
        """Creates the search bar, main scrollable data table, and delete action button."""
        # Top Search Bar Panel
        search_panel = ttk.Frame(parent)
        search_panel.pack(fill=tk.X, pady=(0, 10))
        
        lbl_search = ttk.Label(search_panel, text="🔍 Search:", font=("Arial", 10, "bold"))
        lbl_search.pack(side=tk.LEFT, padx=(0, 5))
        
        self.ent_search = ttk.Entry(search_panel, width=35)
        self.ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ent_search.bind("<KeyRelease>", self.on_search_keypress)
        
        btn_clear = ttk.Button(search_panel, text="Clear", command=self.clear_search, width=8)
        btn_clear.pack(side=tk.LEFT, padx=(5, 0))
        
        # Central Table Card Frame
        table_card = ttk.Frame(parent, style="Card.TFrame", padding=2)
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Treeview Columns
        columns = ("name", "fb_name", "department")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="Full Name", anchor=tk.W)
        self.tree.heading("fb_name", text="Exact Facebook Name", anchor=tk.W)
        self.tree.heading("department", text="Department", anchor=tk.W)
        
        self.tree.column("name", width=220, anchor=tk.W)
        self.tree.column("fb_name", width=220, anchor=tk.W)
        self.tree.column("department", width=120, anchor=tk.W)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bottom Action Bar
        action_bar = ttk.Frame(parent, padding=(0, 10, 0, 0))
        action_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        lbl_note = ttk.Label(action_bar, text="*Changes made are saved instantly to staff.json", font=("Arial", 9, "italic"))
        lbl_note.pack(side=tk.LEFT)
        
        btn_delete = ttk.Button(
            action_bar, 
            text="❌ Delete Selected Staff", 
            style="Danger.TButton", 
            command=self.delete_selected_staff
        )
        btn_delete.pack(side=tk.RIGHT, ipady=2)

    # ----------------------------------------------------
    # Action Functions
    # ----------------------------------------------------
    def refresh_table(self, filter_query=""):
        """Populates or filters treeview table with staff list."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        query = filter_query.lower().strip()
        
        # Sort staff list alphabetically by name for premium grid display
        sorted_list = sorted(self.staff_list, key=lambda s: s.get("name", "").lower())
        
        for staff in sorted_list:
            name = staff.get("name", "")
            fb_name = staff.get("facebook_name", "")
            dept = staff.get("department", "")
            
            # Apply search filter
            if not query or query in name.lower() or query in fb_name.lower() or query in dept.lower():
                self.tree.insert("", tk.END, values=(name, fb_name, dept))

    def refresh_stats(self):
        """Calculates and renders statistics in the left panel stats card."""
        total = len(self.staff_list)
        self.lbl_total_staff.config(text=f"Total Staff: {total}")
        
        # Count by department
        dept_counts = {}
        for staff in self.staff_list:
            d = staff.get("department", "Unknown")
            dept_counts[d] = dept_counts.get(d, 0) + 1
            
        # Format stats text
        stats_lines = []
        # Sort departments alphabetically for aesthetics
        for d in sorted(dept_counts.keys()):
            stats_lines.append(f"• {d}: {dept_counts[d]}")
            
        stats_display_str = "\n".join(stats_lines) if stats_lines else "No staff data loaded."
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, stats_display_str)
        self.stats_text.config(state=tk.DISABLED)

    def add_staff_member(self):
        """Form submission logic to insert a new staff member."""
        name = self.ent_name.get().strip()
        fb_name = self.ent_fb_name.get().strip()
        dept = self.cmb_dept.get()
        
        # Validation
        if not name:
            messagebox.showwarning("Validation Error", "Full Name is required!")
            self.ent_name.focus()
            return
            
        if not fb_name:
            messagebox.showwarning("Validation Error", "Facebook Display Name is required!")
            self.ent_fb_name.focus()
            return
            
        # Check for duplicates (by exact FB name)
        for staff in self.staff_list:
            if staff.get("facebook_name", "").lower() == fb_name.lower():
                messagebox.showerror("Duplicate Record", f"A staff member with the Facebook name '{fb_name}' already exists!")
                return
                
        # Append new member
        new_staff = {
            "name": name,
            "facebook_name": fb_name,
            "department": dept
        }
        
        self.staff_list.append(new_staff)
        self.save_staff_data()
        
        # Clear fields
        self.ent_name.delete(0, tk.END)
        self.ent_fb_name.delete(0, tk.END)
        self.cmb_dept.set("Social Media")
        
        # Refresh visuals
        self.ent_search.delete(0, tk.END)
        self.refresh_table()
        
        messagebox.showinfo("Success", f"Successfully added '{name}' to the roster!")

    def delete_selected_staff(self):
        """Deletes selected staff member in treeview table."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a staff member from the table to delete.")
            return
            
        # Extract name and facebook name from selected row
        values = self.tree.item(selected_item, "values")
        name = values[0]
        fb_name = values[1]
        
        # Double check confirmation
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete '{name}' ({fb_name}) from the PMD staff roster?"
        )
        
        if confirm:
            # Remove from list
            self.staff_list = [s for s in self.staff_list if s.get("facebook_name") != fb_name]
            self.save_staff_data()
            
            # Refresh Table
            self.refresh_table(self.ent_search.get())
            messagebox.showinfo("Deleted", f"Successfully removed '{name}' from the roster.")

    def on_search_keypress(self, event):
        """Real-time filter as the user types in the search box."""
        query = self.ent_search.get()
        self.refresh_table(query)

    def clear_search(self):
        """Clears search box and resets table filters."""
        self.ent_search.delete(0, tk.END)
        self.refresh_table()


if __name__ == "__main__":
    # Create Tkinter application window
    root = tk.Tk()
    app = PMDAdminDashboard(root)
    root.mainloop()
