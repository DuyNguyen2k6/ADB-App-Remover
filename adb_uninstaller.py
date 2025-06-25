import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QListWidget,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class ADBUninstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADB App Uninstaller")
        self.resize(370, 520)
        self.setWindowIcon(QIcon("app_icon.ico"))  # <-- Thêm icon cho cửa sổ

        self.all_packages = []

        # Title label
        title = QLabel("ADB App Uninstaller")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Search box
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Tìm kiếm ứng dụng...")
        self.search_entry.textChanged.connect(self.search_package)

        # List widget for showing package list
        self.listwidget = QListWidget()
        self.listwidget.setSelectionMode(self.listwidget.SelectionMode.MultiSelection)

        # Buttons layout
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Tải lại")
        self.btn_refresh.clicked.connect(self.refresh_list)
        self.btn_uninstall = QPushButton("Gỡ app đã chọn")
        self.btn_uninstall.clicked.connect(self.uninstall_selected)

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_uninstall)

        # Status label
        self.status_label = QLabel("Đang chờ thao tác...")
        self.status_label.setStyleSheet("color: blue;")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addWidget(self.search_entry)
        main_layout.addWidget(self.listwidget)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        # Load package list at start
        self.refresh_list()

    def get_installed_packages(self):
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

    def uninstall_package(self, pkg):
        cmd = ["adb", "shell", "pm", "uninstall", "-k", "--user", "0", pkg]
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.strip()
        if "Success" in output:
            return True, f"Gỡ thành công: {pkg}"
        else:
            return False, f"Lỗi hoặc không thể gỡ: {pkg} - {output}"

    def refresh_list(self):
        self.status_label.setText("Đang tải danh sách...")
        QApplication.processEvents()  # Update UI

        pkgs, err = self.get_installed_packages()
        if err:
            QMessageBox.critical(self, "Lỗi", err)
            self.status_label.setText(err)
            self.all_packages = []
            self.listwidget.clear()
            return

        self.all_packages = pkgs
        self.update_listbox(self.all_packages)
        self.status_label.setText(f"Đã tải {len(pkgs)} app.")

    def update_listbox(self, pkg_list):
        self.listwidget.clear()
        for pkg in pkg_list:
            item = QListWidgetItem(pkg)
            self.listwidget.addItem(item)
        self.status_label.setText(f"Hiển thị {len(pkg_list)} app.")

    def search_package(self):
        keyword = self.search_entry.text().strip().lower()
        if not self.all_packages:
            return
        if keyword == "":
            self.update_listbox(self.all_packages)
        else:
            filtered = [pkg for pkg in self.all_packages if keyword in pkg.lower()]
            self.update_listbox(filtered)

    def uninstall_selected(self):
        selected_items = self.listwidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn app để gỡ.")
            return
        pkgs = [item.text() for item in selected_items]

        reply = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn chắc chắn muốn gỡ {len(pkgs)} app?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        ok, fail = 0, 0
        for pkg in pkgs:
            success, msg = self.uninstall_package(pkg)
            if success:
                ok += 1
            else:
                fail += 1
            self.status_label.setText(msg)
            QApplication.processEvents()

        QMessageBox.information(self, "Kết quả", f"Thành công: {ok}\nLỗi: {fail}")
        self.refresh_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ADBUninstaller()
    window.show()
    sys.exit(app.exec())
