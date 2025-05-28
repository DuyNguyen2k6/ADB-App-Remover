import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, END, MULTIPLE

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
    status_var.set("Đang tải danh sách...")
    root.update_idletasks()
    pkgs, err = get_installed_packages()
    if err:
        messagebox.showerror("Lỗi", err)
        status_var.set(err)
        all_packages = []
        return
    all_packages = pkgs
    update_listbox(all_packages)
    status_var.set(f"Đã tải {len(pkgs)} app.")

def update_listbox(pkg_list):
    listbox.delete(0, END)
    for pkg in pkg_list:
        listbox.insert(END, pkg)
    status_var.set(f"Hiển thị {len(pkg_list)} app.")

def search_package(event=None):
    keyword = search_entry.get().strip().lower()
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
        status_var.set(msg)
        root.update_idletasks()
    messagebox.showinfo("Kết quả", f"Thành công: {ok}\nLỗi: {fail}")
    refresh_list()

root = tk.Tk()
root.title("ADB App Uninstaller")
root.geometry("370x520")
root.resizable(False, False)

tk.Label(root, text="ADB App Uninstaller", font=("Arial", 13, "bold")).pack(pady=7)

# Search
search_entry = tk.Entry(root)
search_entry.pack(fill="x", padx=10, pady=(0, 7))
search_entry.bind("<KeyRelease>", search_package)

# Listbox + scrollbar
listbox = Listbox(root, selectmode=MULTIPLE)
listbox.pack(fill="both", expand=True, padx=10, pady=(0, 7))

# Button row
btn_frame = tk.Frame(root)
btn_frame.pack(pady=4)
tk.Button(btn_frame, text="Tải lại", width=10, command=refresh_list).pack(side="left", padx=3)
tk.Button(btn_frame, text="Gỡ app đã chọn", width=15, command=uninstall_selected).pack(side="left", padx=3)

# Status
status_var = tk.StringVar(value="Đang chờ thao tác...")
tk.Label(root, textvariable=status_var, fg="blue").pack(fill="x", padx=10, pady=3)

all_packages = []
refresh_list()
root.mainloop()
