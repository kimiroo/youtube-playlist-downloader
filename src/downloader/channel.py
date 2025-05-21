import os
from typing import Optional

import requests
import yt_dlp # type: ignore
import magic
from rich.console import Console as RichConsole

import src.config as config
import src.util.string_utils as string_utils
from src.exceptions import UnsupportedFileTypeError, ProfileImageDownloadError, NoProfileImageError, GetProfileImageURLError
from src.db.db_manager import DatabaseManager
from src.util.file_types import mime_to_extension
    
def download_channel_profile_image(channel_handle: str,
                                   url: str,
                                   db_manager: DatabaseManager,
                                   console: Optional[RichConsole] = None) -> None:
    """
    Downloads a channel's profile image with automatic extension detection.

    The downloaded image's filename and the channel handle are registered in the DB.

    Args:
        channel_handle (str): The unique handle of the channel (e.g., "@username").
        url (str): The direct URL of the channel's profile image.
        db_manager (DatabaseManager): An instance of the `DBManager` to save the image filename.
        console (Optional[RichConsole]): `rich.console.Console` for styled output.

    Raises:
        UnsupportedFileTypeError: If the downloaded image's file type is not supported.
        ProfileImageDownloadError: If an error occurs during the image download process.
    """
    _console = console if console else RichConsole()

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        content = b""  # Accumulate the downloaded content
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                content += chunk

        mime_type: Optional[str] = magic.from_buffer(content, mime=True)
        extension = mime_to_extension(mime_type)

        if not extension:
            raise UnsupportedFileTypeError(message="Could not determine file extension", file_type=mime_type)
        
        image_name = f"{string_utils.clean_filename(channel_handle)}.{extension}"
        image_path = os.path.join(config.ICON_DIR, image_name)

        with open(image_path, "wb") as f:
            f.write(content)

        db_manager.save_channel_image_filename(channel_handle=channel_handle, image_filename=image_name)

    except Exception as e:
        raise ProfileImageDownloadError(url=url, original_exception=e)
    
def get_channel_profile_url(channel_handle: str, console: Optional[RichConsole] = None) -> str:
    """
    Retrieves the profile image URL for a given channel handle.

    Args:
        channel_handle (str): The unique handle of the channel (e.g., "@username").
        console (Optional[RichConsole]): `rich.console.Console` for styled output.

    Returns:
        str: The direct URL to the channel's profile image.

    Raises:
        NoProfileImageError: If no profile image URL is found for the channel.
        GetProfileImageURLError: If an error occurs during the process of fetching the URL (e.g., network issue, parsing error).
    """
    _console = console if console else RichConsole()

    # Explicitly type ydl as yt_dlp.YoutubeDL
    ydl: yt_dlp.YoutubeDL = yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True, "playlist_items": "1"})
    try:
        uploader_url = f"https://www.youtube.com/{channel_handle}"
        info = ydl.extract_info(uploader_url, download=False) # type: ignore
        thumbnails = info.get("thumbnails", []) # type: ignore
        for thumbnail in thumbnails: # type: ignore
            if thumbnail.get("id") == "avatar_uncropped": # type: ignore
                _console.print(f"  [bold cyan]✔ Successfully fetched channel profile for:[/bold cyan] {channel_handle}")
                return thumbnail.get("url") # type: ignore
        if thumbnails:
            # fallback to the last thumbnail if avatar_uncropped is not found
            return thumbnails[-1].get("url") # type: ignore
        
        _console.print(f"  [red]✖ Error fetching channel profile:[/red] No profile available.")
        raise NoProfileImageError(channel_handle=channel_handle)
    
    except Exception as e:
        _console.print(f"  [red]✖ Error fetching channel profile image:[/red] {e}")
        raise GetProfileImageURLError(channel_handle=channel_handle, original_exception=e)