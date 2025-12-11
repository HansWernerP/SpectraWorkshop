"""Main entry point for SpectraWorkshop application"""

import sys
from PySide6.QtWidgets import QApplication
from src.spectra_workshop.ui.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("SpectraWorkshop")
    app.setOrganizationName("SpectraWorkshop")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
