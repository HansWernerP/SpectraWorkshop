"""Main window with MDI interface"""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QMdiArea,
    QDockWidget,
    QTextEdit,
    QListWidget,
    QToolBar,
    QStatusBar,
    QFileDialog,
    QMessageBox,
    QTableView,
)
from .dataframe_table_model import DataFrameTableModel


class MainWindow(QMainWindow):
    """Main application window with MDI interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpectraWorkshop")
        self.setGeometry(100, 100, 1200, 800)

        # Set icon path
        self.icon_path = Path(__file__).parent.parent / "resources" / "icons"

        # Create MDI area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)

        # Setup UI components
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        self._create_dock_widgets()

    def _create_menus(self):
        """Create menu bar with File and View menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Import CSV action
        import_action = QAction("&Import CSV", self)
        import_action.setShortcut("Ctrl+I")
        import_action.setStatusTip("Import data from CSV file")
        import_action.triggered.connect(self._import_csv)
        file_menu.addAction(import_action)

        # Export CSV action
        export_action = QAction("&Export CSV", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Export data to CSV file")
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Tile windows action
        tile_action = QAction(self._get_icon("application_tile_horizontal.png"), "&Tile", self)
        tile_action.setStatusTip("Tile MDI windows")
        tile_action.triggered.connect(self._set_tile_view)
        view_menu.addAction(tile_action)

        # Cascade windows action
        cascade_action = QAction(self._get_icon("application_cascade.png"), "&Cascade", self)
        cascade_action.setStatusTip("Cascade MDI windows")
        cascade_action.triggered.connect(self._set_cascade_view)
        view_menu.addAction(cascade_action)

        # Tabbed view action
        tabbed_action = QAction(self._get_icon("application_tabbed.png"), "Ta&bbed", self)
        tabbed_action.setStatusTip("Switch to tabbed view mode")
        tabbed_action.triggered.connect(self._set_tabbed_view)
        view_menu.addAction(tabbed_action)

        # view_menu.addSeparator()
        #
        # # Subwindow view action (reset to default)
        # subwindow_action = QAction(self._get_icon("application.png"), "&Sub-Window View", self)
        # subwindow_action.setStatusTip("Switch to sub-window view mode")
        # subwindow_action.triggered.connect(self._set_subwindow_view)
        # view_menu.addAction(subwindow_action)

    def _create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Import action
        import_action = QAction("Import CSV", self)
        import_action.setStatusTip("Import data from CSV file")
        import_action.triggered.connect(self._import_csv)
        toolbar.addAction(import_action)

        # Export action
        export_action = QAction("Export CSV", self)
        export_action.setStatusTip("Export data to CSV file")
        export_action.triggered.connect(self._export_csv)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        # New MDI window action
        new_window_action = QAction("New Window", self)
        new_window_action.setStatusTip("Create a new MDI window")
        new_window_action.triggered.connect(self._create_new_mdi_window)
        toolbar.addAction(new_window_action)

    def _create_statusbar(self):
        """Create status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    def _create_dock_widgets(self):
        """Create two dock widgets on the left side"""
        # First dock widget (top)
        dock1 = QDockWidget("Properties", self)
        dock1.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Content for first dock widget
        dock1_content = QTextEdit()
        dock1_content.setPlaceholderText("Properties panel...")
        dock1.setWidget(dock1_content)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock1)

        # Second dock widget (bottom)
        dock2 = QDockWidget("Files", self)
        dock2.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Content for second dock widget
        dock2_content = QListWidget()
        dock2_content.addItems(["File 1", "File 2", "File 3"])
        dock2.setWidget(dock2_content)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock2)

        # Store references
        self.dock1 = dock1
        self.dock2 = dock2

    def _create_new_mdi_window(self):
        """Create a new MDI sub-window"""
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Enter text here...")

        sub_window = self.mdi_area.addSubWindow(text_edit)
        sub_window.setWindowTitle(f"Document {self.mdi_area.subWindowList().__len__()}")
        sub_window.show()

        self.statusbar.showMessage(f"Created new window: {sub_window.windowTitle()}", 3000)

    def _import_csv(self):
        """Import data from CSV file"""
        from ..data.csv_import import import_csv_with_groups, get_column_groups

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                self.statusbar.showMessage(f"Importing: {file_path}", 3000)

                # Import CSV with group classification
                df = import_csv_with_groups(file_path)

                # Get group information
                groups = get_column_groups(df)

                # Build info message
                info_lines = [f"CSV file imported successfully!",
                             f"Total rows: {len(df)}",
                             f"Total columns: {len(df.columns)}",
                             "",
                             "Column groups:"]

                for group, cols in sorted(groups.items()):
                    info_lines.append(f"  {group}: {len(cols)} columns")

                QMessageBox.information(
                    self,
                    "Import CSV",
                    "\n".join(info_lines)
                )

                # Display DataFrame in new MDI window
                self._display_dataframe_in_mdi(df, file_path)

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Error importing CSV file:\n{str(e)}"
                )

    def _export_csv(self):
        """Export data to CSV file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.statusbar.showMessage(f"Exporting: {file_path}", 3000)
            # TODO: Implement CSV export logic
            QMessageBox.information(
                self,
                "Export CSV",
                f"Export functionality will be implemented.\nSelected file: {file_path}"
            )

    def _get_icon(self, icon_name):
        """Get icon from resources/icons directory"""
        icon_file = self.icon_path / icon_name
        if icon_file.exists():
            return QIcon(str(icon_file))
        return QIcon()  # Return empty icon if file not found

    def _set_tabbed_view(self):
        """Switch MDI area to tabbed view mode"""
        self.mdi_area.setViewMode(QMdiArea.TabbedView)
        self.statusbar.showMessage("Switched to tabbed view", 2000)

    # def _set_subwindow_view(self):
    #     """Switch MDI area to sub-window view mode"""
    #     self.mdi_area.setViewMode(QMdiArea.SubWindowView)
    #     self.statusbar.showMessage("Switched to sub-window view", 2000)

    def _set_tile_view(self):
        self.mdi_area.setViewMode(QMdiArea.SubWindowView)
        self.mdi_area.tileSubWindows()
        self.statusbar.showMessage("Switched to tile view", 2000)

    def _set_cascade_view(self):
        self.mdi_area.setViewMode(QMdiArea.SubWindowView)
        self.mdi_area.cascadeSubWindows()
        self.statusbar.showMessage("Switched to cascade view", 2000)

    def _display_dataframe_in_mdi(self, df, file_path):
        """
        Display pandas DataFrame in a new MDI window with QTableView

        Args:
            df: pandas DataFrame with MultiIndex columns (group, column_name)
            file_path: Path to the CSV file (used for window title)
        """
        # Create table view
        table_view = QTableView()

        # Create and set the custom model
        model = DataFrameTableModel(df)
        table_view.setModel(model)

        # Adjust table view settings
        table_view.setAlternatingRowColors(False)  # Disable alternating colors
        table_view.horizontalHeader().setStretchLastSection(False)
        table_view.setSelectionBehavior(QTableView.SelectRows)
        table_view.setSelectionMode(QTableView.SingleSelection)

        # Create MDI sub-window
        sub_window = self.mdi_area.addSubWindow(table_view)

        # Set window title to filename without extension
        file_name = Path(file_path).stem
        sub_window.setWindowTitle(file_name)

        # Show and resize window
        sub_window.show()
        sub_window.resize(1000, 600)

        self.statusbar.showMessage(f"Displaying data: {file_name}", 3000)
