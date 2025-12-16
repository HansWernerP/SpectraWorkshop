"""CSV import functionality with column group classification"""

import pandas as pd
import numpy as np
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


def consolidate_x_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolidate all 'x' group columns into a single column containing numpy arrays.
    The new column name is composed from the first and last x-column names.

    Args:
        df: DataFrame with MultiIndex columns (group, column_name)

    Returns:
        DataFrame with consolidated x columns as numpy vectors
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()

    # Check if 'x' group exists
    if 'x' not in df.columns.get_level_values('group'):
        return result_df

    # Get all x columns
    x_cols = df['x'].columns.tolist()

    if len(x_cols) == 0:
        return result_df

    # Create new column name from first and last x column
    first_col = x_cols[0]
    last_col = x_cols[-1]
    new_col_name = f"{first_col}-{last_col}"

    # Convert x columns to numpy arrays for each row
    x_data = df['x'].values
    consolidated_data = [row for row in x_data]

    # Remove all x columns
    result_df = result_df.drop('x', axis=1, level=0)

    # Add new consolidated column
    result_df[('x', new_col_name)] = consolidated_data

    return result_df


def expand_x_columns(df: pd.DataFrame, original_column_names: list[str]) -> pd.DataFrame:
    """
    Expand a consolidated x column (containing numpy arrays) back into individual columns.

    Args:
        df: DataFrame with consolidated x column containing numpy arrays
        original_column_names: List of original column names for the x group

    Returns:
        DataFrame with expanded x columns
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()

    # Check if 'x' group exists
    if 'x' not in df.columns.get_level_values('group'):
        return result_df

    # Get the x column (should be only one)
    x_cols = df['x'].columns.tolist()

    if len(x_cols) != 1:
        raise ValueError(f"Expected exactly one x column, but found {len(x_cols)}")

    # Get the consolidated column data
    consolidated_col = x_cols[0]
    x_data = df[('x', consolidated_col)]

    # Convert numpy arrays back to individual columns
    expanded_data = np.stack(x_data.values)

    # Check dimensions match
    if expanded_data.shape[1] != len(original_column_names):
        raise ValueError(
            f"Data dimension ({expanded_data.shape[1]}) does not match "
            f"number of column names ({len(original_column_names)})"
        )

    # Remove consolidated column
    result_df = result_df.drop(('x', consolidated_col), axis=1)

    # Add expanded columns
    for i, col_name in enumerate(original_column_names):
        result_df[('x', col_name)] = expanded_data[:, i]

    # Reorder columns to maintain original structure
    # Get all groups in order
    all_cols = []
    for group in result_df.columns.get_level_values('group').unique():
        if group == 'x':
            all_cols.extend([('x', col) for col in original_column_names])
        else:
            all_cols.extend([(group, col) for col in result_df[group].columns])

    # Remove duplicates while preserving order
    seen = set()
    ordered_cols = []
    for col in all_cols:
        if col not in seen:
            seen.add(col)
            ordered_cols.append(col)

    result_df = result_df[ordered_cols]

    return result_df
