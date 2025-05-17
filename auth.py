import tkinter as tk
from tkinter import messagebox
from db import connect_db, create_tables
import dashboard

def login_screen():
    create_tables()
    auth = tk.Tk()
    auth.title("Admin Login")
    auth.geometry("400x200")
    auth.configure(bg="#e8f5e9")

    tk.Label(auth, text="Username").pack(pady=5)
    username_entry = tk.Entry(auth)
    username_entry.pack(fill="x", padx=20)

    tk.Label(auth, text="Password").pack(pady=5)
    password_entry = tk.Entry(auth, show="*")
    password_entry.pack(fill="x", padx=20)

    def login():
        user = username_entry.get()
        pw = password_entry.get()
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, pw))
        if cur.fetchone():
            auth.destroy()
            dashboard.load_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    tk.Button(auth, text="Login", command=login, bg="green", fg="white").pack(pady=10, fill="x", padx=20)

    auth.mainloop()
