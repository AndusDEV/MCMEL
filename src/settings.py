import json, os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QFileDialog, QMessageBox,
    QGroupBox, QSizePolicy, QSpacerItem, QScrollArea, QWidget
)
from src.update_check import __version__

CONFIG_FILE = "games_config.json"
DEFAULTS = {
  "Minecraft: Java Edition": {
    "type": "flatpak",
    "exec_path": "org.prismlauncher.PrismLauncher",
    "instances_path": "/home/user/.var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances",
    "show": True
  },
  "Minecraft: Bedrock Edition": {
    "type": "flatpak",
    "exec_path": "io.mrarm.mcpelauncher",
    "show": True
  },
  "Minecraft Dungeons": {
    "show": False
  },
  "Minecraft Legends": {
    "show": False
  },
  "Minecraft: Story Mode": {
    "version": "steam",
    "exec_path": "1",
    "show": False
  },
  "Minecraft Story Mode: Season 2": {
    "version": "steam",
    "exec_path": "2",
    "show": False
  },
  "Minecraft: Xbox 360 Edition": {
    "exec_path": "/path/to/xenia",
    "rom_path": "/path/to/minecraft",
    "show": False
  },
  "Minecraft Classic": {
    "show": False
  },
  "update_check": True,
}

GAMES = [
    "Minecraft: Java Edition",
    "Minecraft: Bedrock Edition",
    "Minecraft Dungeons",
    "Minecraft Legends",
    "Minecraft: Story Mode",
    "Minecraft Story Mode: Season 2",
    "Minecraft: Xbox 360 Edition",
    "Minecraft Classic"
]
DESCRIPTIONS = {
    "Minecraft: Java Edition": "Utilizes MultiMC (or forks)",
    "Minecraft: Bedrock Edition": "Utilizes MCPE Launcher",
    "Minecraft Dungeons": "Launches Steam version",
    "Minecraft Legends": "Launches Steam version",
    "Minecraft: Story Mode": "Launches Steam or Lutris (GOG) version",
    "Minecraft Story Mode: Season 2": "Launches Steam or Lutris (GOG) version",
    "Minecraft: Xbox 360 Edition": "Utilizes Xenia Emulator",
    "Minecraft Classic": "Launches classic.minecraft.net in the browser"
}

def load_config():
    cfg = DEFAULTS.copy()
    if os.path.exists(CONFIG_FILE):
        user_cfg = json.load(open(CONFIG_FILE))
        for key, val in user_cfg.items():
            if key in GAMES:
                cfg.setdefault(key, {})
                cfg[key].update(val)
            elif key == "update_check":
                cfg["update_check"] = val
    return cfg

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(800, 540)
        self.config = load_config()
        self.edits = {}
        self.init_ui()

    def init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        inner = QWidget()
        layout = QVBoxLayout(inner)
        scroll.setWidget(inner)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)

        games_config_label = QLabel("Games Config:")
        games_config_label.setObjectName("SettingsLabel")
        games_config_label.setWordWrap(True)
        layout.addWidget(games_config_label)

        info_label = QLabel(
            'Read the <a href="https://github.com/AndusDEV/MCMEL/blob/master/README.md#how-to-configure-the-editions">project\'s README on GitHub</a> \
            to learn how to configure the launcher.'
            )
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        for game in GAMES:
            cfg = self.config.get(game, {})
            box = QGroupBox(game)
            box_layout = QVBoxLayout(box)

            description_label = QLabel(DESCRIPTIONS.get(game, ""))
            description_label.setWordWrap(True)
            description_label.setObjectName("SettingsDescriptionLabel")
            box_layout.addWidget(description_label)

            # Show checkbox
            show_cb = QCheckBox("Show in launcher")
            show_cb.setChecked(cfg.get("show", False))
            box_layout.addWidget(show_cb)
            self.edits[(game, "show")] = show_cb

            # Launcher type (only for Java and Bedrock)
            if game in ["Minecraft: Java Edition", "Minecraft: Bedrock Edition"]:
                rb_native, rb_flatpak = QRadioButton("Native"), QRadioButton("Flatpak")
                bg = QButtonGroup(self)
                bg.addButton(rb_native); bg.addButton(rb_flatpak)
                (rb_flatpak if cfg.get("type") == "flatpak" else rb_native).setChecked(True)

                row = QHBoxLayout()
                row.addWidget(QLabel("Launcher Type:"))
                row.addWidget(rb_native)
                row.addWidget(rb_flatpak)
                box_layout.addLayout(row)
                self.edits[(game, "type")] = bg
            
            # Game version (only for Story Mode 1/2)
            if game in ["Minecraft: Story Mode", "Minecraft Story Mode: Season 2"]:
                rb_steam, rb_lutris = QRadioButton("Steam"), QRadioButton("Lutris (GOG)")
                bg = QButtonGroup(self)
                bg.addButton(rb_steam); bg.addButton(rb_lutris)
                (rb_lutris if cfg.get("version") == "lutris" else rb_steam).setChecked(True)
                
                row = QHBoxLayout()
                row.addWidget(QLabel("Game Version:"))
                row.addWidget(rb_steam)
                row.addWidget(rb_lutris)
                box_layout.addLayout(row)
                self.edits[(game, "version")] = bg

            # Exec path
            if "exec_path" in cfg:
                le = QLineEdit(cfg.get("exec_path", ""))
                btn = QPushButton("Browse")
                btn.clicked.connect(lambda _, le=le: self._browse(le, QFileDialog.getOpenFileName))
                row = QHBoxLayout()
                row.addWidget(QLabel("Executable:"))
                row.addWidget(le)
                row.addWidget(btn)
                box_layout.addLayout(row)
                self.edits[(game, "exec_path")] = le

            # Instances path (Java only)
            if game == "Minecraft: Java Edition":
                le = QLineEdit(cfg.get("instances_path", ""))
                btn = QPushButton("Browse")
                btn.clicked.connect(lambda _, le=le: self._browse(le, QFileDialog.getExistingDirectory))
                row = QHBoxLayout()
                row.addWidget(QLabel("Instances Path:"))
                row.addWidget(le)
                row.addWidget(btn)
                box_layout.addLayout(row)
                self.edits[(game, "instances_path")] = le

            # ROM path (Emulator only)
            if game == "Minecraft: Xbox 360 Edition":
                le = QLineEdit(cfg.get("rom_path", ""))
                btn = QPushButton("Browse")
                btn.clicked.connect(lambda _, le=le: self._browse(le, QFileDialog.getExistingDirectory))
                row = QHBoxLayout()
                row.addWidget(QLabel("ROM Path:"))
                row.addWidget(le)
                row.addWidget(btn)
                box_layout.addLayout(row)
                self.edits[(game, "rom_path")] = le

            layout.addWidget(box)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        mcmel_settings_label = QLabel("MCMEL Settings:")
        mcmel_settings_label.setObjectName("SettingsLabel")
        mcmel_settings_label.setWordWrap(True)
        layout.addWidget(mcmel_settings_label)

        self.update_check = QCheckBox("Check For Updates On Start")
        self.update_check.setChecked(self.config.get("update_check", True))
        layout.addWidget(self.update_check)

        github_label = QLabel('<a href="https://github.com/AndusDEV/MCMEL">MCMEL GitHub Repo</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setWordWrap(True)
        layout.addWidget(github_label)

        version_label = QLabel(f"Launcher Version: <strong>{__version__}</strong>")
        version_label.setWordWrap(True)
        layout.addWidget(version_label)

        btn_row = QHBoxLayout()
        btn_save, btn_cancel = QPushButton("Save"), QPushButton("Cancel")
        btn_save.clicked.connect(self.on_save)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addStretch(); btn_row.addWidget(btn_save); btn_row.addWidget(btn_cancel)
        outer_layout.addLayout(btn_row)

    def _browse(self, lineedit, func):
        result = func(self, "Select")[0] if func == QFileDialog.getOpenFileName else func(self, "Select")
        if result:
            lineedit.setText(result)

    def on_save(self):
        for (game, key), widget in self.edits.items():
            if key == "show":
                val = widget.isChecked()
            elif key == "type":
                val = "flatpak" if widget.buttons()[1].isChecked() else "native"
            elif key == "version":
                val = "lutris" if widget.buttons()[1].isChecked() else "steam"
            else:
                val = widget.text().strip()
            self.config.setdefault(game, {})[key] = val
        
        self.config["update_check"] = self.update_check.isChecked()

        try:
            save_config(self.config)
            QMessageBox.information(self, "Saved", "Configuration saved."
                                                   "\nRestart the launcher for new editions to show up.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
