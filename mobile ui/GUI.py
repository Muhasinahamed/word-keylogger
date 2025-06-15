import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import firebase_admin
from firebase_admin import credentials, db

# 🔑 Initialize Firebase RTDB
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-default-rtdb.firebaseio.com/'  # Replace with your actual database URL
})
ref = db.reference("logs")

# 🔄 Fetch Logs from RTDB
def fetch_logs():
    snapshot = ref.get()
    logs = []

    if snapshot:
        for key in sorted(snapshot.keys(), key=lambda k: snapshot[k].get("timestamp", "")):
            data = snapshot[key]
            logs.append([
                data.get("timestamp", ""),
                data.get("word", ""),
                f"{data.get('typing_time', 0):.2f}s"
            ])
    return logs

# 🔁 Track already inserted logs
inserted_keys = set()

# 🔁 Refresh Table
def refresh_gui():
    logs = fetch_logs()
    last_item = None

    for entry in logs:
        log_id = f"{entry[0]}-{entry[1]}"  # Use timestamp-word as unique ID

        if log_id not in inserted_keys:
            last_item = tree.insert("", "end", values=entry)
            inserted_keys.add(log_id)

    # Auto-scroll to last new entry
    if last_item:
        tree.see(last_item)

    # ⏱️ Check for updates frequently
    root.after(100, refresh_gui)

# 🖼 GUI Setup
root = tk.Tk()
root.title("RTDB Typing Log Viewer")
root.geometry("900x600")

font_small = tkFont.Font(family="Courier New", size=9)

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

x_scroll = ttk.Scrollbar(frame, orient="horizontal")
y_scroll = ttk.Scrollbar(frame, orient="vertical")

tree = ttk.Treeview(
    frame,
    columns=("Time", "Word", "Speed"),
    show='headings',
    xscrollcommand=x_scroll.set,
    yscrollcommand=y_scroll.set
)

tree.heading("Time", text="Timestamp")
tree.heading("Word", text="Word")
tree.heading("Speed", text="Time Taken (s)")

tree.column("Time", anchor="center", width=300, minwidth=200)
tree.column("Word", anchor="center", width=600, minwidth=300)
tree.column("Speed", anchor="center", width=200, minwidth=120)

style = ttk.Style()
style.configure("Treeview", font=("Courier New", 9), rowheight=80)
style.configure("Treeview.Heading", font=("Courier New", 9, "bold"))

tree.grid(row=0, column=0, sticky="nsew")
y_scroll.config(command=tree.yview)
x_scroll.config(command=tree.xview)

y_scroll.grid(row=0, column=1, sticky='ns')
x_scroll.grid(row=1, column=0, sticky='ew')

frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

# 🚀 Start GUI Loop
refresh_gui()
root.mainloop()
