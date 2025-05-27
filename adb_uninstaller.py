import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, MULTIPLE, END

# Theme settings
BG_COLOR = "#f3f4f6"
CARD_BG = "#ffffff"
PRIMARY_COLOR = "#2563eb"
DANGER_COLOR = "#ef4444"
FONT = ("Segoe UI", 11)
TITLE_FONT = ("Segoe UI Semibold", 16)
ENTRY_BG = "#e5e7eb"

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
root.title("🪟 Gỡ app Android - Windows 11 Style")
root.geometry("480x640")
root.configure(bg=BG_COLOR)
root.minsize(420, 540)

# Title
title_label = tk.Label(root, text="GỠ APP ANDROID", font=TITLE_FONT, bg=BG_COLOR, fg=PRIMARY_COLOR, pady=8)
title_label.pack(pady=(16, 8))

# Card frame
card = tk.Frame(root, bg=CARD_BG, bd=0, relief="flat")
card.pack(fill="both", expand=True, padx=28, pady=(0, 18))

# Search bar
search_frame = tk.Frame(card, bg=CARD_BG)
search_frame.pack(fill="x", padx=12, pady=(16, 10))

search_var = tk.StringVar()
search_entry = tk.Entry(
    search_frame, textvariable=search_var, font=FONT, bg=ENTRY_BG, 
    relief="flat", borderwidth=8, fg="#555", justify="left"
)
search_entry.pack(side="left", fill="x", expand=True, ipady=7)
search_entry.insert(0, "Nhập từ khóa để tìm app...")

def clear_placeholder(event):
    if search_entry.get() == "Nhập từ khóa để tìm app...":
        search_entry.delete(0, END)
        search_entry.config(fg="#222")
search_entry.bind("<FocusIn>", clear_placeholder)
search_entry.bind("<KeyRelease>", search_package)

search_btn = tk.Button(
    search_frame, text="Tìm kiếm", font=FONT, bg=PRIMARY_COLOR, fg="white", 
    activebackground="#1d4ed8", relief="flat", bd=0, padx=18, pady=5, 
    command=search_package, cursor="hand2"
)
search_btn.pack(side="right", padx=8)

# Listbox
list_frame = tk.Frame(card, bg=CARD_BG)
list_frame.pack(fill="both", expand=True, padx=0, pady=(0, 10))

scroll = Scrollbar(list_frame, bg=CARD_BG)
scroll.pack(side="right", fill="y", pady=4)

listbox = Listbox(
    list_frame, selectmode=MULTIPLE, yscrollcommand=scroll.set,
    font=FONT, relief="flat", borderwidth=0, highlightthickness=1,
    highlightbackground="#e5e7eb", bg="#f9fafb", fg="#222",
    selectbackground=PRIMARY_COLOR, selectforeground="white",
    activestyle="none"
)
listbox.pack(fill="both", expand=True, pady=4, ipadx=4, ipady=4)
scroll.config(command=listbox.yview)

# Button row
btn_frame = tk.Frame(card, bg=CARD_BG)
btn_frame.pack(fill="x", padx=8, pady=(0, 14))

refresh_btn = tk.Button(
    btn_frame, text="⟳ Tải lại", font=FONT, bg="#f1f5f9", fg=PRIMARY_COLOR,
    activebackground="#dbeafe", activeforeground=PRIMARY_COLOR,
    relief="flat", bd=0, padx=12, pady=8, cursor="hand2", command=refresh_list
)
refresh_btn.pack(side="left", padx=(0, 12), ipadx=2, ipady=1)

uninstall_btn = tk.Button(
    btn_frame, text="🗑 Gỡ app đã chọn", font=FONT, bg=DANGER_COLOR, fg="white",
    activebackground="#dc2626", relief="flat", bd=0, padx=14, pady=8, 
    cursor="hand2", command=uninstall_selected
)
uninstall_btn.pack(side="right", padx=(12, 0), ipadx=2, ipady=1)

# Status label
status_label = tk.Label(
    root, text="Đang chờ thao tác...", font=("Segoe UI", 10),
    fg="#3b82f6", bg=BG_COLOR, pady=9
)
status_label.pack(fill="x", padx=28, pady=(0, 10))

# Data holder
all_packages = []

refresh_list()
root.mainloop()
