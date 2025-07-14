import configparser
import json
import os
import subprocess
from os.path import isdir, join

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QMessageBox, QComboBox, QListView, QStyledItemDelegate
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic
from src.game_info import GameInfo
from src.settings import SettingsDialog
from src.update_check import UpdateCheckDialog, check_for_update

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
            GameInfo("Minecraft Classic", "./assets/images/mcc.png", "./assets/icons/game/mcc.png")
        ]
        self.games = [g for g in self.games if self.game_configs.get(g.name, {}).get("show", False)]

        self.load_stylesheet("assets/ui/style.qss")

        update_available, message = check_for_update()
        
        if update_available:
            dialog = UpdateCheckDialog(message, stylesheet=self.styleSheet())
            dialog.exec_()
        else:
            print(message)

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

        self.settings_button = QPushButton("Settings")
        self.settings_button.setIcon(QIcon("./assets/icons/settings.png"))
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setObjectName("SettingsButton")

        left_layout.addWidget(self.game_list)
        left_layout.addWidget(self.settings_button, alignment=Qt.AlignLeft)

        # Right Panel
        right_layout = QVBoxLayout()
        self.game_image = QLabel()
        self.game_image.setFixedSize(700, 394)
        self.game_image.setScaledContents(True)

        self.account_selector = QComboBox()
        self.account_selector.hide()
        account_delegate = QStyledItemDelegate()
        self.account_selector.setView(QListView())
        self.account_selector.view().setItemDelegate(account_delegate)

        self.version_selector = QComboBox()
        self.version_selector.hide()
        version_delegate = QStyledItemDelegate()
        self.version_selector.setView(QListView())
        self.version_selector.view().setItemDelegate(version_delegate)

        self.launch_button = QPushButton("Launch")
        self.launch_button.setIcon(QIcon("./assets/icons/launch.png"))
        self.launch_button.setIconSize(self.launch_button.sizeHint())

        self.open_launcher_button = QPushButton("Open Original Launcher")
        self.open_launcher_button.setIcon(QIcon("./assets/icons/open_launcher.png"))
        self.open_launcher_button.setIconSize(self.launch_button.sizeHint())
        self.open_launcher_button.hide()
        self.open_launcher_button.clicked.connect(self.open_original_launcher)

        right_layout.addWidget(self.game_image)
        right_layout.addWidget(self.version_selector)
        right_layout.addWidget(self.launch_button)
        right_layout.addStretch()

        bottom_right_layout = QHBoxLayout()
        bottom_right_layout.addWidget(self.account_selector, alignment=Qt.AlignLeft)
        bottom_right_layout.addStretch()
        bottom_right_layout.addWidget(self.open_launcher_button, alignment=Qt.AlignRight)
        right_layout.addLayout(bottom_right_layout)

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
            self.account_selector.show()
            self.version_selector.show()
            self.populate_accounts_java()
            self.populate_versions_java()
            self.open_launcher_button.show()
        elif game.name == "Minecraft: Bedrock Edition":
            self.account_selector.hide()
            self.version_selector.show()
            self.populate_versions_bedrock()
            self.open_launcher_button.show()
        else:
            self.account_selector.hide()
            self.version_selector.hide()
            self.open_launcher_button.hide()


    def populate_accounts_java(self):
        self.account_selector.clear()
        config = self.game_configs.get(self.games[self.current_game_index].name, {})
        instances_path = config.get("instances_path", "")
        accounts_path = os.path.join(os.path.dirname(instances_path), "accounts.json")

        if not accounts_path or not os.path.exists(accounts_path):
            self.account_selector.addItem("No accounts found")
            return
        
        with open(accounts_path) as f:
            accounts = json.load(f)

        profile_names = []

        for account in accounts.get("accounts", []):
            profile = account.get("profile")
            if profile and "name" in profile:
                profile_names.append(profile["name"])

        self.account_selector.addItems(profile_names)


    def populate_versions_java(self):
        self.version_selector.clear()
        config = self.game_configs.get(self.games[self.current_game_index].name, {})
        path = config.get("instances_path", "")

        if not path or not os.path.exists(path):
            self.version_selector.addItem("No instances found")
            return

        default_icon = QIcon("./assets/icons/game/mcje.png")
        versions = sorted(
            f for f in os.listdir(path)
            if isdir(join(path, f)) and not f.startswith(".")
        )

        if not versions:
            self.version_selector.addItem("No instances found")
            return

        for v in versions:
            vp = join(path, v)
            for folder in ("minecraft", ".minecraft"):
                icon_file = join(vp, folder, "icon.png")
                if os.path.exists(icon_file):
                    break
            else:
                icon_file = None
            self.version_selector.addItem(QIcon(icon_file) if icon_file else default_icon, v)

    def populate_versions_bedrock(self):
        self.version_selector.clear()
        config = self.game_configs.get(self.games[self.current_game_index].name, {})

        flatpak = os.path.expanduser("~/.var/app/io.mrarm.mcpelauncher/data/mcpelauncher/profiles/profiles.ini")
        native = os.path.expanduser("~/.local/share/mcpelauncher/profiles/profiles.ini")
        ini_path = flatpak if os.path.exists(flatpak) else native if os.path.exists(native) else None

        if not ini_path:
            self.version_selector.addItem("No profiles.ini found")
            return

        ini = configparser.ConfigParser()
        ini.read(ini_path)
        profiles = [s for s in ini.sections() if s != "General"]

        icon = QIcon("./assets/icons/game/mcbe.png")

        if not profiles:
            self.version_selector.addItem("No profiles found")
        else:
            for p in profiles:
                self.version_selector.addItem(icon, p.replace('%20', ' '))

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
        game_version = config.get("version", "steam")
        rom_path = config.get("rom_path", "")

        args = []

        if game.name == "Minecraft: Java Edition":
            instance = self.version_selector.currentText()
            account = self.account_selector.currentText()
            if instance in ("No instances found", "", None):
                QMessageBox.warning(self, "Error", "No valid instance selected.")
                return
            if account in ("No accounts found", "", None):
                QMessageBox.warning(self, "Error", "No valid account selected.")
                return
            args = ["flatpak", "run", exec_path, "-l", instance, "-a", account] if game_type == "flatpak" else [exec_path, "-l", instance, "-a", account]

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

        elif game.name in ["Minecraft: Story Mode"]:
            if game_version == "steam":
                args = ["xdg-open", "steam://run/376870"]
            else:
                args = ["xdg-open", f"lutris:rungameid/{exec_path}"]
        
        elif game.name in ["Minecraft Story Mode: Season 2"]:
            if game_version == "steam":
                args = ["xdg-open", "steam://run/639170"]
            else:
                args = ["xdg-open", f"lutris:rungameid/{exec_path}"]

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

        elif game.name == "Minecraft Classic":
            args = ["xdg-open", "https://classic.minecraft.net"]
        
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
