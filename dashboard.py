import tkinter as tk
from tkinter import ttk, messagebox
from db import connect_db

def load_dashboard():
    global root
    root = tk.Tk()
    root.title("Census Dashboard")
    root.geometry("1200x600")
    root.configure(bg="#e8f5e9")

    tk.Label(root, text="Census Management System", font=("Arial", 18, "bold"), bg="#e8f5e9").pack(pady=10)

    # Stats Frame
    stats_frame = tk.Frame(root, bg="#e8f5e9")
    stats_frame.pack(padx=20, pady=10, fill="x")

    def create_card(parent, title, count, bg_color):
        card = tk.Frame(parent, bg=bg_color, width=200, height=70)
        card.pack_propagate(0)
        card.pack(side="left", padx=10, pady=5, expand=True, fill="x")

        tk.Label(card, text=title, bg=bg_color, fg="white", font=("Arial", 12, "bold")).pack()
        tk.Label(card, text=str(count), bg=bg_color, fg="white", font=("Arial", 16, "bold")).pack()

    def render_cards():
        for widget in stats_frame.winfo_children():
            widget.destroy()

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM people")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM people WHERE gender = 'Male'")
        male = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM people WHERE gender = 'Female'")
        female = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM people WHERE gender = 'Other'")
        other = cur.fetchone()[0]

        conn.close()

        create_card(stats_frame, "Total People", total, "#388e3c")
        create_card(stats_frame, "Total Male", male, "#1976d2")
        create_card(stats_frame, "Total Female", female, "#d81b60")
        create_card(stats_frame, "Other Gender", other, "#6d4c41")

    # Table Frame
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=20)

    columns = ("ID", "Name", "Age", "Gender", "Permanent Address", "Present Address")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.pack(fill="both", expand=True)

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM people")
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
        render_cards()

    def person_form(mode="add", data=None):
        def save_or_update():
            name = entry_name.get().strip()
            age = entry_age.get().strip()
            gender = gender_var.get().strip()
            permanent = entry_perm.get().strip()
            present = entry_pres.get().strip()
            if not name or not age or not permanent or not present:
                messagebox.showwarning("Validation", "All fields are required.")
                return
            try:
                int(age)
            except ValueError:
                messagebox.showwarning("Validation", "Age must be a number.")
                return

            conn = connect_db()
            cur = conn.cursor()
            if mode == "add":
                cur.execute("INSERT INTO people (name, age, gender, permanent_address, present_address) VALUES (?, ?, ?, ?, ?)",
                            (name, age, gender, permanent, present))
            else:
                cur.execute("UPDATE people SET name=?, age=?, gender=?, permanent_address=?, present_address=? WHERE id=?",
                            (name, age, gender, permanent, present, data[0]))
            conn.commit()
            conn.close()
            top.destroy()
            refresh_table()

        top = tk.Toplevel(root)
        top.title("Add Person" if mode == "add" else "Edit Person")
        top.geometry("400x400")
        top.configure(bg="#f0f0f0")

        def full_input(label_text, default_val=""):
            tk.Label(top, text=label_text, anchor="w").pack(fill="x", padx=10)
            entry = tk.Entry(top)
            entry.insert(0, default_val)
            entry.pack(fill="x", padx=10, pady=5)
            return entry

        entry_name = full_input("Name", data[1] if data else "")
        entry_age = full_input("Age", data[2] if data else "")

        gender_var = tk.StringVar()
        gender_var.set(data[3] if data else "Male")
        tk.Label(top, text="Gender", anchor="w").pack(fill="x", padx=10)
        gender_menu = tk.OptionMenu(top, gender_var, "Male", "Female", "Other")
        gender_menu.pack(fill="x", padx=10, pady=5)

        entry_perm = full_input("Permanent Address", data[4] if data else "")
        entry_pres = full_input("Present Address", data[5] if data else "")

        btn_color = "#4CAF50" if mode == "add" else "#f44336"
        tk.Button(top, text="Save" if mode == "add" else "Update", command=save_or_update,
                  bg=btn_color, fg="white").pack(pady=15, padx=10, fill="x")

    def add_person():
        person_form("add")

    def edit_person():
        selected = tree.focus()
        if selected:
            data = tree.item(selected)['values']
            person_form("edit", data)

    def delete_person():
        selected = tree.focus()
        if selected:
            data = tree.item(selected)['values']
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM people WHERE id=?", (data[0],))
            conn.commit()
            conn.close()
            refresh_table()

    def logout():
        root.destroy()
        import auth
        auth.login_screen()

    # Action Buttons
    action_frame = tk.Frame(root, bg="#e8f5e9")
    action_frame.pack(pady=10)

    tk.Button(action_frame, text="➕ Add Person", command=add_person, bg="green", fg="white", width=15).pack(side="left", padx=5)
    tk.Button(action_frame, text="✏️ Edit Selected", command=edit_person, bg="orange", fg="white", width=15).pack(side="left", padx=5)
    tk.Button(action_frame, text="🚮 Delete Selected", command=delete_person, bg="red", fg="white", width=15).pack(side="left", padx=5)
    tk.Button(action_frame, text="🚪Logout", command=logout, bg="black", fg="white", width=15).pack(side="left", padx=5)

    refresh_table()
    root.mainloop()
