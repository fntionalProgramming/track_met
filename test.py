import tkinter as tk
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteEntry
import pandas as pd

# Global data storage
athlete_data = {}

def load_csv():
    file_path = r"C:\Users\admin\track_meet\twilight meet 4\athlete_schedule.csv"
    try:
        df = pd.read_csv(file_path)
        df = df[df['Team'].str.upper() == "EHC"]

        # Clean column names
        df.columns = [col.strip() for col in df.columns]

        for _, row in df.iterrows():
            athlete = row['Name'].strip().title()
            event = row['Event'].strip()
            time = row.get('Time', 'TBD')
            location = row.get('Location', 'Unknown')

            if pd.isna(time):
                time = 'TBD'
            if pd.isna(location):
                location = 'Unknown'

            if athlete not in athlete_data:
                athlete_data[athlete] = []
            athlete_data[athlete].append((time, event, location))

        # Update autocomplete list
        name_entry.set_completion_list(sorted(athlete_data.keys()))

        messagebox.showinfo("Success", "CSV loaded from hardcoded path.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV:\n{e}")

def show_athlete_schedule():
    name = name_entry.get().strip().title()
    if not name:
        messagebox.showerror("Input Error", "Please enter an athlete's name.")
        return
    if name not in athlete_data:
        messagebox.showwarning("Not Found", f"No data found for {name}")
        return

    schedule = sorted(athlete_data[name], key=lambda x: x[0])
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Schedule for {name}:\n")
    for time, event, location in schedule:
        result_text.insert(tk.END, f"{time} - {event} @ {location}\n")

def show_master_schedule():
    combined = []
    for athlete, events in athlete_data.items():
        for time, event, location in events:
            combined.append((time, athlete, event, location))

    try:
        combined.sort(key=lambda x: pd.to_datetime(x[0], errors='coerce'))
    except Exception:
        combined.sort(key=lambda x: x[0])  # fallback if time parsing fails

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Master Schedule:\n")
    for time, athlete, event, location in combined:
        result_text.insert(tk.END, f"{time} - {athlete}: {event} @ {location}\n")

# GUI setup
root = tk.Tk()
root.title("ttm")
root.geometry("700x500")

frame = tk.Frame(root)
frame.pack(pady=10)

load_btn = tk.Button(frame, text="Load Trackie CSV", command=load_csv)
load_btn.grid(row=0, column=0, padx=5)

name_label = tk.Label(frame, text="Athlete Name:")
name_label.grid(row=0, column=1, padx=5)

# Initialize with empty list to avoid NoneType error
name_entry = AutocompleteEntry(frame, width=30, completevalues=[])
name_entry.grid(row=0, column=2, padx=5)

athlete_btn = tk.Button(frame, text="Get Athlete Schedule", command=show_athlete_schedule)
athlete_btn.grid(row=0, column=3, padx=5)

master_btn = tk.Button(frame, text="Show Master Schedule", command=show_master_schedule)
master_btn.grid(row=0, column=4, padx=5)

result_text = tk.Text(root, wrap=tk.WORD, height=25)
result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
