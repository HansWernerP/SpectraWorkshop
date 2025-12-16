"""Custom table model for displaying pandas DataFrame with group-based coloring"""

import pandas as pd
import numpy as np
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor


class DataFrameTableModel(QAbstractTableModel):
    """Table model for pandas DataFrame with group-based background colors"""

    # Define pastel colors for each group
    GROUP_COLORS = {
        'sid': QColor(255, 253, 208),      # Light yellow-beige
        'x': QColor(173, 216, 230),        # Light blue
        'y': QColor(198, 239, 206),        # Light green
        'cat': QColor(255, 218, 185),      # Light orange
        'unknown': QColor(211, 211, 211),  # Light grey
        'prd': QColor(221, 160, 221),      # Light purple/plum
        'md': QColor(240, 230, 140),       # Light khaki
        'time': QColor(255, 182, 193),     # Light pink
    }

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        """
        Initialize the table model with a pandas DataFrame

        Args:
            dataframe: pandas DataFrame with MultiIndex columns (group, column_name)
            parent: Parent QObject
        """
        super().__init__(parent)
        self._dataframe = dataframe

        # Extract group information from MultiIndex
        if isinstance(dataframe.columns, pd.MultiIndex):
            self._groups = dataframe.columns.get_level_values('group').tolist()
            self._column_names = dataframe.columns.get_level_values('column').tolist()
        else:
            # Fallback if no MultiIndex
            self._groups = ['unknown'] * len(dataframe.columns)
            self._column_names = dataframe.columns.tolist()

    def rowCount(self, parent=QModelIndex()):
        """Return number of rows"""
        if parent.isValid():
            return 0
        return len(self._dataframe)

    def columnCount(self, parent=QModelIndex()):
        """Return number of columns"""
        if parent.isValid():
            return 0
        return len(self._dataframe.columns)

    def data(self, index, role=Qt.DisplayRole):
        """Return data for the given index and role"""
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            # Get value from DataFrame
            value = self._dataframe.iloc[row, col]

            # Handle different data types
            # Check for numpy array first, before pd.isna()
            if isinstance(value, np.ndarray):
                # For numpy arrays, display only the first value
                if len(value) > 0:
                    first_val = value[0]
                    if isinstance(first_val, float):
                        return f"{first_val:.6f}"
                    else:
                        return str(first_val)
                else:
                    return "[]"
            elif pd.isna(value):
                return ""
            elif isinstance(value, float):
                return f"{value:.6f}"  # Format floats with 6 decimal places
            else:
                return str(value)

        elif role == Qt.BackgroundRole:
            # Get group for this column
            group = self._groups[col]

            # Return color based on group
            return self.GROUP_COLORS.get(group, QColor(255, 255, 255))

        elif role == Qt.TextAlignmentRole:
            # Align numbers to the right
            value = self._dataframe.iloc[row, col]
            if isinstance(value, np.ndarray):
                # For numpy arrays, check first element
                if len(value) > 0 and isinstance(value[0], (int, float)):
                    return Qt.AlignRight | Qt.AlignVCenter
            elif isinstance(value, (int, float)) and not pd.isna(value):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # Return column name
                return str(self._column_names[section])
            else:
                # Return row number (1-based)
                return str(section + 1)

        elif role == Qt.BackgroundRole and orientation == Qt.Horizontal:
            # Color the column headers with the same color as the group
            group = self._groups[section]
            return self.GROUP_COLORS.get(group, QColor(255, 255, 255))

        return None

    def flags(self, index):
        """Return item flags"""
        if not index.isValid():
            return Qt.NoItemFlags

        # Make items selectable and enabled, but not editable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
