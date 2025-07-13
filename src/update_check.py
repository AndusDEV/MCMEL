import sys
import subprocess
import requests
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
)

__version__ = "v0.2.0"
GITHUB_API = "https://api.github.com/repos/AndusDEV/MCMEL/releases/latest"

def normalize_version(tag):
    if tag.startswith("v"):
        tag = tag[1:]
    return tuple(int(p) for p in tag.split("."))

def check_for_update():
    try:
        response = requests.get(GITHUB_API, timeout=5)
        if response.status_code != 200:
            return False, f"GitHub API returned {response.status_code}"
        
        data = response.json()
        latest_tag = data.get("tag_name")
        if not latest_tag:
            return False, "No tag_name in release data."
        
        if normalize_version(latest_tag) > normalize_version(__version__):
            return True, f"New version available: {latest_tag}"
        else:
            return False, f"You are up to date ({__version__})."
    
    except Exception as e:
        return False, str(e)

class UpdateCheckDialog(QDialog):
    def __init__(self, message, stylesheet=None):
        super().__init__()
        self.setWindowTitle("Update Checker")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)
        self.label = QLabel(message, self)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.btn_open = QPushButton("Open GitHub Releases", self)
        self.btn_open.clicked.connect(self.open_github)
        layout.addWidget(self.btn_open)

        if stylesheet:
            self.setStyleSheet(stylesheet)

    def open_github(self):
        subprocess.Popen(["xdg-open", "https://github.com/AndusDEV/MCMEL/releases"])
        self.accept()