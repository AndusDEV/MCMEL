import configparser
import json
import os
import subprocess
from os.path import isdir, join

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QMessageBox, QComboBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic
from src.game_info import GameInfo
from src.settings import SettingsDialog

class Launcher(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        with open("games_config.json", "r") as f:
            self.game_configs = json.load(f)

        self.games = [
            GameInfo("Minecraft: Java Edition", "./assets/images/mcje.png", "./assets/icons/game/mcje.png"),
            GameInfo("Minecraft: Bedrock Edition", "./assets/images/mcbe.png", "./assets/icons/game/mcbe.png"),
            GameInfo("Minecraft Dungeons", "./assets/images/mcd.png", "./assets/icons/game/mcd.png"),
            GameInfo("Minecraft Legends", "./assets/images/mcl.png", "./assets/icons/game/mcl.png"),
            GameInfo("Minecraft: Story Mode", "./assets/images/mcsm.jpg", "./assets/icons/game/mcsm.png"),
            GameInfo("Minecraft Story Mode: Season 2", "./assets/images/mcsm2.jpg", "./assets/icons/game/mcsm2.png"),
            GameInfo("Minecraft: Xbox 360 Edition", "./assets/images/mc360.png", "./assets/icons/game/mc360.png"),
        ]

        self.games = [g for g in self.games if self.game_configs.get(g.name, {}).get("show", False)]

        self.current_game_index = -1
        self.setup_ui()
        self.game_list.setCurrentRow(0)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Left Sidebar
        left_layout = QVBoxLayout()
        self.game_list = QListWidget()
        self.game_list.setFixedWidth(300)

        for game in self.games:
            item = QListWidgetItem(QIcon(game.icon_path), game.name)
            self.game_list.addItem(item)

        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon("./assets/icons/settings.png"))
        self.settings_button.setText("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setObjectName("SettingsButton")

        left_layout.addWidget(self.game_list)
        left_layout.addWidget(self.settings_button, alignment=Qt.AlignLeft)

        # Right Panel
        right_layout = QVBoxLayout()
        self.game_image = QLabel()
        self.game_image.setFixedSize(700, 394)
        self.game_image.setScaledContents(True)

        self.version_selector = QComboBox()
        self.version_selector.hide()

        self.launch_button = QPushButton("Launch")

        self.open_launcher_button = QPushButton()
        self.open_launcher_button.setIcon(QIcon("./assets/icons/open_launcher.png"))
        self.open_launcher_button.setIconSize(self.launch_button.sizeHint())
        self.open_launcher_button.setText("Open Original Launcher")
        self.open_launcher_button.hide()
        self.open_launcher_button.clicked.connect(self.open_original_launcher)

        right_layout.addWidget(self.game_image)
        right_layout.addWidget(self.version_selector)
        right_layout.addWidget(self.launch_button)
        right_layout.addStretch()
        right_layout.addWidget(self.open_launcher_button, alignment=Qt.AlignRight)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        self.setWindowTitle("Minecraft: Multi-Edition Launcher")
        self.setFixedSize(1000, 640)
        self.load_stylesheet("assets/ui/style.qss")
        self.game_list.currentRowChanged.connect(self.on_game_selected)
        self.launch_button.clicked.connect(self.on_launch_clicked)

    def on_game_selected(self, row):
        if not (0 <= row < len(self.games)):
            return

        game = self.games[row]
        self.current_game_index = row

        pixmap = QPixmap(game.image_path)
        self.game_image.setPixmap(pixmap if not pixmap.isNull() else QPixmap())
        if pixmap.isNull():
            self.game_image.setText("No Image")

        if game.name == "Minecraft: Java Edition":
            self.version_selector.show()
            self.populate_versions_java()
            self.open_launcher_button.show()
        elif game.name == "Minecraft: Bedrock Edition":
            self.version_selector.show()
            self.populate_versions_bedrock()
            self.open_launcher_button.show()
        else:
            self.version_selector.hide()
            self.open_launcher_button.hide()

    def populate_versions_java(self):
        self.version_selector.clear()
        config = self.game_configs.get(self.games[self.current_game_index].name, {})
        path = config.get("instances_path", "")

        if not path or not os.path.exists(path):
            self.version_selector.addItem("No instances found")
            return

        versions = [f for f in os.listdir(path) if isdir(join(path, f)) and f != ".LAUNCHER_TEMP"]
        self.version_selector.addItems(sorted(versions) if versions else ["No instances found"])

    def populate_versions_bedrock(self):
        self.version_selector.clear()
        game = self.games[self.current_game_index]
        config = self.game_configs.get(game.name, {})

        flatpak_path = os.path.expanduser("~/.var/app/io.mrarm.mcpelauncher/data/mcpelauncher/profiles/profiles.ini")
        native_path = os.path.expanduser("~/.local/share/mcpelauncher/profiles/profiles.ini")

        ini_path = flatpak_path if os.path.exists(flatpak_path) else native_path if os.path.exists(
            native_path) else None
        if not ini_path:
            self.version_selector.addItem("No profiles.ini found")
            return

        ini = configparser.ConfigParser()
        ini.read(ini_path)

        profiles = [section for section in ini.sections() if section != "General"]

        if not profiles:
            self.version_selector.addItem("No profiles found")
        else:
            decoded = [section.replace('%20', ' ') for section in profiles]
            self.version_selector.addItems(decoded)

    def open_original_launcher(self):
        if self.current_game_index == -1:
            return

        game = self.games[self.current_game_index]
        config = self.game_configs.get(game.name, {})
        exec_path = config.get("exec_path", "")
        game_type = config.get("type", "native")

        if not exec_path:
            QMessageBox.warning(self, "Error", "No exec path configured.")
            return

        try:
            command = ["flatpak", "run", exec_path] if game_type == "flatpak" else [exec_path]
            subprocess.Popen(command)
        except Exception as e:
            QMessageBox.critical(self, "Launcher Error", str(e))

    def on_launch_clicked(self):
        if self.current_game_index == -1:
            return

        game = self.games[self.current_game_index]
        config = self.game_configs.get(game.name, {})
        exec_path = config.get("exec_path")
        game_type = config.get("type", "native")
        rom_path = config.get("rom_path", "")

        if not exec_path:
            QMessageBox.warning(self, "Error", "No exec path configured.")
            return

        args = []

        if game.name == "Minecraft: Java Edition":
            instance = self.version_selector.currentText()
            if instance in ("No instances found", "", None):
                QMessageBox.warning(self, "Error", "No valid instance selected.")
                return
            args = ["flatpak", "run", exec_path, "-l", instance] if game_type == "flatpak" else [exec_path, "-l", instance]

        elif game.name == "Minecraft: Bedrock Edition":
            version = self.version_selector.currentText()
            if version in ("No versions found", "", None):
                QMessageBox.warning(self, "Error", "No valid version selected.")
                return
            args = ["flatpak", "run", exec_path, "-p", version] if game_type == "flatpak" else [exec_path, "-p", version]

        elif game.name == "Minecraft Dungeons":
            args = ["xdg-open", "steam://run/1672970"]
        elif game.name == "Minecraft Legends":
            args = ["xdg-open", "steam://run/1928870"]

        elif game.name in ["Minecraft: Story Mode", "Minecraft Story Mode: Season 2"]:
            QMessageBox.warning(self, "Not Implemented", "This game is not implemented yet.")
            return

        elif game.name == "Minecraft: Xbox 360 Edition":
            parent = os.path.dirname(os.path.realpath(exec_path))
            proton = os.path.expanduser("~/.steam/steam/steamapps/common/Proton - Experimental/proton")
            compat = os.path.expanduser("~/.mcmel")
            env = os.environ.copy()
            env.update({
                "STEAM_COMPAT_DATA_PATH": compat,
                "STEAM_COMPAT_CLIENT_INSTALL_PATH": compat,
                "PROTON_LOG": "1"
            })
            args = [proton, "run", exec_path, rom_path]
            subprocess.Popen(args, cwd=parent, env=env)
            return
        else:
            QMessageBox.warning(self, "Unknown Game Type", f"Handling for {game.name} is not defined.")
            return

        try:
            subprocess.Popen(args)
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", str(e))

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_():
            with open("games_config.json") as f:
                self.game_configs = json.load(f)
            self.games = [g for g in self.games if self.game_configs.get(g.name, {}).get("show", False)]
            self.game_list.clear()
            for game in self.games:
                self.game_list.addItem(QListWidgetItem(QIcon(game.icon_path), game.name))
            self.game_list.setCurrentRow(0)

    def load_stylesheet(self, path):
        try:
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Failed to load stylesheet: {e}")