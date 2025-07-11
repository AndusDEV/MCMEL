import sys
from PyQt5.QtWidgets import QApplication
from src.launcher import Launcher

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec_())
