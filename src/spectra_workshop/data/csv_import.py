"""CSV import functionality with column group classification"""

import pandas as pd
from pathlib import Path


def classify_column_group(column_name: str, is_first_col: bool, is_before_x_group: bool) -> str:
    """
    Classify a column into one of the groups: sid, x, y, cat, prd, md, time, unknown

    Args:
        column_name: The name of the column
        is_first_col: Whether this is the first column
        is_before_x_group: Whether this column appears before the first x-group column

    Returns:
        Group name as string
    """
    col_str = str(column_name)

    # Rule 2: First column before x-group gets 'sid'
    if is_first_col and is_before_x_group:
        return 'sid'

    # Rule 1: Numeric column names belong to 'x' group
    try:
        float(col_str)
        return 'x'
    except ValueError:
        pass

    # Rule 3: Ends with "(LAB)" -> y group
    if col_str.endswith('(LAB)'):
        return 'y'

    # Rule 4: Ends with "(NIR)" -> prd group
    if col_str.endswith('(NIR)'):
        return 'prd'

    # Rule 5: Starts with "MD value" -> md group
    if col_str.startswith('MD value'):
        return 'md'

    # Rule 6: Starts with "Start", "Time", or "Date" -> time group
    if col_str.startswith(('Start', 'Time', 'Date')):
        return 'time'

    # Rule 7: Starts with "Product" -> cat group
    if col_str.startswith('Product'):
        return 'cat'

    # Rule 8: All others -> unknown
    return 'unknown'


def import_csv_with_groups(file_path: str | Path) -> pd.DataFrame:
    """
    Import CSV file and create DataFrame with MultiIndex columns (group, column_name)

    Args:
        file_path: Path to the CSV file

    Returns:
        pandas DataFrame with MultiIndex columns
    """
    # Read CSV file
    df = pd.read_csv(file_path)

    # Find first x-group column
    first_x_idx = None
    for idx, col in enumerate(df.columns):
        try:
            float(str(col))
            first_x_idx = idx
            break
        except ValueError:
            continue

    # Classify all columns
    groups = []
    for idx, col in enumerate(df.columns):
        is_first_col = (idx == 0)
        is_before_x = (first_x_idx is None or idx < first_x_idx)
        group = classify_column_group(col, is_first_col, is_before_x)
        groups.append(group)

    # Create MultiIndex with (group, column_name)
    df.columns = pd.MultiIndex.from_tuples(
        [(group, col) for group, col in zip(groups, df.columns)],
        names=['group', 'column']
    )

    return df


def get_group_columns(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """
    Get all columns belonging to a specific group

    Args:
        df: DataFrame with MultiIndex columns
        group: Group name (e.g., 'x', 'y', 'sid')

    Returns:
        DataFrame containing only the specified group's columns
    """
    return df[group]


def get_column_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Get a dictionary of all groups and their column names

    Args:
        df: DataFrame with MultiIndex columns

    Returns:
        Dictionary mapping group names to lists of column names
    """
    groups_dict = {}
    for group in df.columns.get_level_values('group').unique():
        groups_dict[group] = df[group].columns.tolist()
    return groups_dict
