import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, MULTIPLE, END

# Win10 theme settings
BG_COLOR = "#f2f2f2"
CARD_BG = "#e6e6e6"
PRIMARY_COLOR = "#0078D7"
DANGER_COLOR = "#e81123"
FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI Semibold", 15)
ENTRY_BG = "#ffffff"

def get_installed_packages():
    try:
        cmd = ["adb", "shell", "pm", "list", "packages", "--user", "0"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return [], "ADB chưa chạy hoặc chưa kết nối thiết bị!"
        lines = result.stdout.strip().split('\n')
        packages = [line.replace("package:", "").strip() for line in lines if line]
        return packages, ""
    except Exception as e:
        return [], f"Lỗi: {str(e)}"

def uninstall_package(pkg):
    cmd = ["adb", "shell", "pm", "uninstall", "-k", "--user", "0", pkg]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()
    if "Success" in output:
        return True, f"Gỡ thành công: {pkg}"
    else:
        return False, f"Lỗi hoặc không thể gỡ: {pkg} - {output}"

def refresh_list():
    global all_packages
    listbox.delete(0, END)
    status_label.config(text="Đang tải danh sách...")
    root.update_idletasks()
    pkgs, err = get_installed_packages()
    if err:
        messagebox.showerror("Lỗi", err)
        status_label.config(text=err)
        all_packages = []
        return
    all_packages = pkgs
    update_listbox(all_packages)
    status_label.config(text=f"Đã tải {len(pkgs)} app.")

def update_listbox(pkg_list):
    listbox.delete(0, END)
    for pkg in pkg_list:
        listbox.insert(END, pkg)
    status_label.config(text=f"Hiển thị {len(pkg_list)} app.")

def search_package(event=None):
    keyword = search_var.get().strip().lower()
    if not all_packages:
        return
    if keyword == "":
        update_listbox(all_packages)
    else:
        filtered = [pkg for pkg in all_packages if keyword in pkg.lower()]
        update_listbox(filtered)

def uninstall_selected():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Vui lòng chọn app để gỡ.")
        return
    pkgs = [listbox.get(i) for i in selected]
    if not messagebox.askyesno("Xác nhận", f"Bạn chắc chắn muốn gỡ {len(pkgs)} app?"):
        return
    ok, fail = 0, 0
    for pkg in pkgs:
        success, msg = uninstall_package(pkg)
        if success:
            ok += 1
        else:
            fail += 1
        status_label.config(text=msg)
        root.update_idletasks()
    messagebox.showinfo("Kết quả", f"Thành công: {ok}\nLỗi: {fail}")
    refresh_list()

root = tk.Tk()
root.title("Gỡ app Android - Windows 10 Style")
root.geometry("440x600")
root.configure(bg=BG_COLOR)
root.minsize(400, 480)

# Title
title_label = tk.Label(root, text="GỠ APP ANDROID", font=TITLE_FONT, bg=BG_COLOR, fg=PRIMARY_COLOR, pady=7)
title_label.pack(pady=(14, 6))

# Card frame
card = tk.Frame(root, bg=CARD_BG, bd=2, relief="groove")
card.pack(fill="both", expand=True, padx=20, pady=(0, 18))

# Search bar
search_frame = tk.Frame(card, bg=CARD_BG)
search_frame.pack(fill="x", padx=10, pady=(14, 8))

search_var = tk.StringVar()
search_entry = tk.Entry(
    search_frame, textvariable=search_var, font=FONT, bg=ENTRY_BG,
    relief="solid", borderwidth=1, fg="#222", justify="left"
)
search_entry.pack(side="left", fill="x", expand=True, ipady=6)
search_entry.insert(0, "....................Nhập từ khóa để tìm app....................")

def clear_placeholder(event):
    if search_entry.get() == "....................Nhập từ khóa để tìm app....................":
        search_entry.delete(0, END)
        search_entry.config(fg="#222")
search_entry.bind("<FocusIn>", clear_placeholder)
search_entry.bind("<KeyRelease>", search_package)

search_btn = tk.Button(
    search_frame, text="Tìm kiếm", font=FONT, bg=PRIMARY_COLOR, fg="white",
    activebackground="#005a9e", relief="flat", bd=1, padx=12, pady=3,
    command=search_package, cursor="hand2"
)
search_btn.pack(side="right", padx=7)

# Listbox
list_frame = tk.Frame(card, bg=CARD_BG)
list_frame.pack(fill="both", expand=True, padx=0, pady=(0, 8))

scroll = Scrollbar(list_frame)
scroll.pack(side="right", fill="y", pady=2)

listbox = Listbox(
    list_frame, selectmode=MULTIPLE, yscrollcommand=scroll.set,
    font=FONT, relief="solid", borderwidth=1, highlightthickness=1,
    highlightbackground="#d1d5db", bg="#fff", fg="#222",
    selectbackground=PRIMARY_COLOR, selectforeground="white",
    activestyle="none"
)
listbox.pack(fill="both", expand=True, pady=2)
scroll.config(command=listbox.yview)

# Button row
btn_frame = tk.Frame(card, bg=CARD_BG)
btn_frame.pack(fill="x", padx=8, pady=(0, 12))

refresh_btn = tk.Button(
    btn_frame, text="⟳ Tải lại", font=FONT, bg="#e1e1e1", fg=PRIMARY_COLOR,
    activebackground="#d1d1d1", activeforeground=PRIMARY_COLOR,
    relief="ridge", bd=1, padx=10, pady=6, cursor="hand2", command=refresh_list
)
refresh_btn.pack(side="left", padx=(0, 10), ipadx=2, ipady=0)

uninstall_btn = tk.Button(
    btn_frame, text="🗑 Gỡ app đã chọn", font=FONT, bg=DANGER_COLOR, fg="white",
    activebackground="#c50f1f", relief="ridge", bd=1, padx=12, pady=6,
    cursor="hand2", command=uninstall_selected
)
uninstall_btn.pack(side="right", padx=(10, 0), ipadx=2, ipady=0)

# Status label
status_label = tk.Label(
    root, text="Đang chờ thao tác...", font=("Segoe UI", 9),
    fg=PRIMARY_COLOR, bg=BG_COLOR, pady=8
)
status_label.pack(fill="x", padx=20, pady=(0, 8))

# Data holder
all_packages = []

refresh_list()
root.mainloop()
