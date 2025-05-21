import os
import re
from typing import Optional

import ffmpeg # type: ignore
from rich.console import Console as RichConsole

from src.exceptions import FileConversionError

def convert_to_ogg(filepath: str, console: Optional[RichConsole] = None) -> str:
    """
    Extracts Ogg audio from a .webm file and saves it to a new .ogg file.

    Args:
        filepath (str): Path of the .webm file to convert.

    Returns:
        str: The full path to the newly created .ogg file.
    
    Raises:
        ValueError: If the input `filepath` does not have a .webm extension.
        FileConversionError: If the file conversion process fails (e.g., ffmpeg error).
    """
    _console = console if console else RichConsole()
    
    new_filepath = None # Initialize
    try:
        # Check if the file has a .webm extension. If not, this function might be misused.
        if not filepath.lower().endswith(".webm"):
            raise ValueError(f"Input file '{filepath}' does not have a .webm extension. Expected .webm for OGG conversion.")
        
        # Generate new filename
        new_filepath = re.sub(r"\.webm$", ".ogg", filepath, flags=re.IGNORECASE)

        # Delete target file if exists
        if os.path.exists(new_filepath):
            os.remove(new_filepath)

        # Convert to ogg and remove old file
        ffmpeg.input(filepath).output(new_filepath, format="ogg", c="copy").run(overwrite_output=True, quiet=True) # type: ignore
        os.remove(filepath)

        _console.print(f"    [bold cyan]✔ Converted to OGG[/bold cyan]")
        return new_filepath
    
    except Exception as e:
        _console.print(f"    [red]✖ Conversion error:[/red] {e}")
        raise FileConversionError(input_path=filepath,
                                  output_path=new_filepath,
                                  original_exception=e)