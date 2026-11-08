import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "cgpa_data.json"

# ---------------------------------------------------------
# Theme / Colors
# ---------------------------------------------------------
DARK = False
COLORS = {
    "light": {
        "bg": "#f0f0f0",
        "frame_bg": "#ffffff",
        "label_fg": "#000000",
        "button_bg": "#e0e0e0",
        "button_fg": "#000000",
        "entry_bg": "#ffffff",
    },
    "dark": {
        "bg": "#2b2b2b",
        "frame_bg": "#3c3f41",
        "label_fg": "#ffffff",
        "button_bg": "#555555",
        "button_fg": "#ffffff",
        "entry_bg": "#4a4a4a",
    }
}

def getc(theme, key):
    return COLORS[theme][key]

# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
subjects = []
semester_results = []

GRADE_POINTS = {
    "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "F": 0
}

# ---------------------------------------------------------
# Persistence
# ---------------------------------------------------------
def load_data():
    global subjects, semester_results
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                subjects = data.get("subjects", [])
                semester_results = data.get("semester_results", [])
        except:
            subjects = []
            semester_results = []

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "subjects": subjects,
            "semester_results": semester_results
        }, f, indent=4)

# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------
def add_subject():
    subject = subject_entry.get().strip()
    credits = credits_entry.get().strip()
    grade = grade_box.get()

    if subject == "" or credits == "" or grade == "":
        messagebox.showwarning("Missing Information", "Please enter subject, credits and grade.")
        return

    try:
        credits = float(credits)
        if credits <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Credits", "Credits must be a positive number.")
        return

    subject_data = {
        "subject": subject,
        "credits": credits,
        "grade": grade,
        "points": GRADE_POINTS[grade]
    }
    subjects.append(subject_data)
    save_data()
    refresh_table()
    clear_subject_fields()

def remove_subject():
    selected = subject_table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a subject.")
        return
    index = int(selected[0])
    del subjects[index]
    save_data()
    refresh_table()

def clear_subject_fields():
    subject_entry.delete(0, tk.END)
    credits_entry.delete(0, tk.END)
    grade_box.set("")

def clear_all_subjects():
    if not subjects:
        return
    answer = messagebox.askyesno("Clear All", "Do you want to remove all subjects?")
    if answer:
        subjects.clear()
        save_data()
        refresh_table()

def refresh_table():
    for item in subject_table.get_children():
        subject_table.delete(item)
    for index, subject in enumerate(subjects):
        subject_table.insert("", tk.END, iid=index, values=(
            subject["subject"], subject["credits"], subject["grade"], subject["points"]
        ))

def calculate_sgpa():
    if not subjects:
        messagebox.showwarning("No Subjects", "Please add subjects first.")
        return
    total_credits = sum(s["credits"] for s in subjects)
    total_points = sum(s["credits"] * s["points"] for s in subjects)
    sgpa = total_points / total_credits
    sgpa_result.config(text=f"{sgpa:.2f}")
    semester_results.append({"credits": total_credits, "sgpa": sgpa})
    save_data()
    refresh_semester_table()
    messagebox.showinfo("SGPA Calculated", f"Your SGPA is {sgpa:.2f}")

def calculate_cgpa():
    if not semester_results:
        messagebox.showwarning("No Semester Data", "Calculate at least one semester SGPA first.")
        return
    total_weighted = sum(s["sgpa"] * s["credits"] for s in semester_results)
    total_credits = sum(s["credits"] for s in semester_results)
    cgpa = total_weighted / total_credits
    cgpa_result.config(text=f"{cgpa:.2f}")

def add_current_semester():
    if not subjects:
        messagebox.showwarning("No Subjects", "Add subjects before saving the semester.")
        return
    total_credits = sum(s["credits"] for s in subjects)
    total_points = sum(s["credits"] * s["points"] for s in subjects)
    sgpa = total_points / total_credits
    semester_results.append({"credits": total_credits, "sgpa": sgpa})
    save_data()
    refresh_semester_table()
    subjects.clear()
    save_data()
    refresh_table()
    sgpa_result.config(text="0.00")
    calculate_cgpa()
    messagebox.showinfo("Semester Added", f"Semester added successfully!\n\nSGPA: {sgpa:.2f}")

def remove_semester():
    selected = semester_table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Select a semester first.")
        return
    index = int(selected[0])
    del semester_results[index]
    save_data()
    refresh_semester_table()
    calculate_cgpa()

def refresh_semester_table():
    for item in semester_table.get_children():
        semester_table.delete(item)
    for index, semester in enumerate(semester_results):
        semester_table.insert("", tk.END, iid=index, values=(
            index + 1, semester["credits"], f"{semester['sgpa']:.2f}"
        ))

def reset_all():
    answer = messagebox.askyesno("Reset", "Reset all subjects and semester data?")
    if answer:
        subjects.clear()
        semester_results.clear()
        save_data()
        refresh_table()
        refresh_semester_table()
        sgpa_result.config(text="0.00")
        cgpa_result.config(text="0.00")

def toggle_theme():
    global DARK
    DARK = not DARK
    theme = "dark" if DARK else "light"
    bg = getc(theme, "bg")
    root.configure(bg=bg)
    title.configure(bg=bg, fg=getc(theme, "label_fg"))
    subtitle.configure(bg=bg, fg=getc(theme, "label_fg"))
    theme_btn.config(text="☀ Light Mode" if DARK else "🌙 Dark Mode")

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
root = tk.Tk()
root.title("Smart CGPA & SGPA Calculator")
root.geometry("900x720")
root.resizable(False, False)

title = tk.Label(root, text="SMART CGPA & SGPA CALCULATOR", font=("Arial", 24, "bold"))
title.pack(pady=(15, 3))

subtitle = tk.Label(root, text="Calculate your academic performance easily", font=("Arial", 11))
subtitle.pack()

theme_btn = tk.Button(root, text="🌙 Dark Mode", command=toggle_theme, width=15)
theme_btn.pack(pady=5)

input_frame = tk.LabelFrame(root, text="Add Subject", padx=10, pady=10)
input_frame.pack(fill="x", padx=30, pady=15)

tk.Label(input_frame, text="Subject:").grid(row=0, column=0, padx=8)
subject_entry = tk.Entry(input_frame, width=22)
subject_entry.grid(row=0, column=1, padx=8)

tk.Label(input_frame, text="Credits:").grid(row=0, column=2, padx=8)
credits_entry = tk.Entry(input_frame, width=10)
credits_entry.grid(row=0, column=3, padx=8)

tk.Label(input_frame, text="Grade:").grid(row=0, column=4, padx=8)
grade_box = ttk.Combobox(input_frame, values=list(GRADE_POINTS.keys()), width=8, state="readonly")
grade_box.grid(row=0, column=5, padx=8)

tk.Button(input_frame, text="Add Subject", width=14, command=add_subject).grid(row=0, column=6, padx=8)

table_frame = tk.Frame(root)
table_frame.pack(pady=5)

columns = ("Subject", "Credits", "Grade", "Grade Point")
subject_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
for column in columns:
    subject_table.heading(column, text=column)
subject_table.column("Subject", width=300)
subject_table.column("Credits", width=120)
subject_table.column("Grade", width=120)
subject_table.column("Grade Point", width=150)
subject_table.pack()

subject_buttons = tk.Frame(root)
subject_buttons.pack(pady=8)

tk.Button(subject_buttons, text="Remove Subject", width=18, command=remove_subject).grid(row=0, column=0, padx=5)
tk.Button(subject_buttons, text="Clear All", width=18, command=clear_all_subjects).grid(row=0, column=1, padx=5)
tk.Button(subject_buttons, text="Calculate SGPA", width=18, command=calculate_sgpa).grid(row=0, column=2, padx=5)

result_frame = tk.Frame(root)
result_frame.pack(pady=10)

tk.Label(result_frame, text="Current SGPA", font=("Arial", 12)).grid(row=0, column=0, padx=60)
sgpa_result = tk.Label(result_frame, text="0.00", font=("Arial", 25, "bold"))
sgpa_result.grid(row=1, column=0)

tk.Label(result_frame, text="Overall CGPA", font=("Arial", 12)).grid(row=0, column=1, padx=60)
cgpa_result = tk.Label(result_frame, text="0.00", font=("Arial", 25, "bold"))
cgpa_result.grid(row=1, column=1)

semester_frame = tk.LabelFrame(root, text="Semester History", padx=10, pady=5)
semester_frame.pack(fill="x", padx=30, pady=5)

semester_table = ttk.Treeview(semester_frame, columns=("Semester", "Credits", "SGPA"), show="headings", height=3)
semester_table.heading("Semester", text="Semester")
semester_table.heading("Credits", text="Credits")
semester_table.heading("SGPA", text="SGPA")
semester_table.column("Semester", width=200)
semester_table.column("Credits", width=200)
semester_table.column("SGPA", width=200)
semester_table.pack()

semester_buttons = tk.Frame(root)
semester_buttons.pack(pady=8)

tk.Button(semester_buttons, text="Add Current Semester", width=22, command=add_current_semester).grid(row=0, column=0, padx=5)
tk.Button(semester_buttons, text="Remove Semester", width=18, command=remove_semester).grid(row=0, column=1, padx=5)
tk.Button(semester_buttons, text="Reset", width=12, command=reset_all).grid(row=0, column=2, padx=5)

load_data()
refresh_table()
refresh_semester_table()
if semester_results:
    calculate_cgpa()

root.mainloop()