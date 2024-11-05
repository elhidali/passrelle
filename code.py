from dataclasses import dataclass
from typing import List, Tuple
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from pathlib import Path

# Constants
EXCEL_ENGINE = 'openpyxl'
COLUMN_WIDTH_PADDING = 2
FLOAT_FORMAT = "%.10f"
EMPTY_CELL_REPRESENTATION = ''
ASCII_A = 65  # ASCII code for 'A'

@dataclass(frozen=True)
class ExcelWorksheetConfig:
    """Configuration for Excel worksheet formatting."""
    float_format: str = FLOAT_FORMAT
    na_rep: str = EMPTY_CELL_REPRESENTATION
    column_padding: int = COLUMN_WIDTH_PADDING

@dataclass(frozen=True)
class ExcelSheet:
    """Represents a sheet in an Excel workbook."""
    dataframe: pd.DataFrame
    name: str

def validate_inputs(sheets: List[ExcelSheet]) -> None:
    """
    Validate input parameters for Excel sheet creation.
    
    Args:
        sheets: List of ExcelSheet objects
        
    Raises:
        ValueError: If the input parameters are invalid
    """
    if not sheets:
        raise ValueError("No sheets provided")
    if len({sheet.name for sheet in sheets}) != len(sheets):
        raise ValueError("Duplicate sheet names found")

def calculate_column_width(series: pd.Series, column_name: str) -> int:
    """
    Calculate the optimal width for a column.
    
    Args:
        series: Column data
        column_name: Name of the column
        
    Returns:
        Optimal column width
    """
    max_value_length = series.astype(str).map(len).max()
    return max(max_value_length, len(column_name))

def adjust_column_widths(worksheet: Worksheet, df: pd.DataFrame) -> None:
    """
    Adjust column widths based on content.
    
    Args:
        worksheet: Excel worksheet
        df: DataFrame containing the data
    """
    for idx, (column_name, column_data) in enumerate(df.items()):
        width = calculate_column_width(column_data, column_name)
        column_letter = chr(ASCII_A + idx)
        worksheet.column_dimensions[column_letter].width = width + COLUMN_WIDTH_PADDING

def write_dataframe_to_excel(
    writer: pd.ExcelWriter,
    sheet: ExcelSheet,
    config: ExcelWorksheetConfig
) -> None:
    """
    Write a single DataFrame to an Excel sheet and format it.
    
    Args:
        writer: Excel writer object
        sheet: ExcelSheet object containing DataFrame and sheet name
        config: Configuration for worksheet formatting
    """
    sheet.dataframe.to_excel(
        writer,
        sheet_name=sheet.name,
        index=False,
        float_format=config.float_format,
        na_rep=config.na_rep
    )
    adjust_column_widths(writer.sheets[sheet.name], sheet.dataframe)

def save_dataframes_to_excel(
    sheets: List[ExcelSheet],
    output_path: Path,
    config: ExcelWorksheetConfig = ExcelWorksheetConfig()
) -> None:
    """
    Save multiple DataFrames to a single Excel file.
    
    Args:
        sheets: List of ExcelSheet objects
        output_path: Path where to save the Excel file
        config: Configuration for worksheet formatting
        
    Raises:
        ValueError: If input validation fails
    """
    validate_inputs(sheets)
    
    with pd.ExcelWriter(output_path, engine=EXCEL_ENGINE) as writer:
        for sheet in sheets:
            write_dataframe_to_excel(writer, sheet, config)

def main() -> None:
    """Example usage of the Excel saving functionality."""
    # Example usage
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'X': [5, 6], 'Y': [7, 8]})
    
    sheets = [
        ExcelSheet(df1, "Sheet1"),
        ExcelSheet(df2, "Sheet2")
    ]
    
    output_path = Path("output.xlsx")
    save_dataframes_to_excel(sheets, output_path)

if __name__ == "__main__":
    main()
