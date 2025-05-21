import os
from typing import Any, Dict, List, Optional, cast

import yt_dlp # type: ignore
from rich.console import Console as RichConsole

import src.config as config
import src.util.string_utils as string_utils
import src.converter.convert as convert
import src.converter.metadata as metadata
from src.db.db_manager import DatabaseManager
from src.exceptions import ConversionMaxRetryAttemptError, DownloadError, FileConversionError

def get_playlist_info(url: str, console: Optional[RichConsole] = None) -> dict[str, Any]:
    """
    Fetches playlist information json from YouTube.

    Args:
        url (str): Playlist URL
    
    Returns:
        dict: Playlist object
    """
    _console = console if console else RichConsole()

    _console.print(f"[bold blue]➜ Fetching playlist:[/bold blue] {url}")

    playlist_info: dict[str, Any] = {}
    
    # Explicitly type ydl as yt_dlp.YoutubeDL
    ydl: yt_dlp.YoutubeDL = yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True})
    playlist_info = ydl.extract_info(url, download=False) # type: ignore

    # Remove empty or faulty entries(e.g. private video) from playlist_info
    raw_entries = cast(Optional[List[Dict[str, Any]]], playlist_info.get("entries"))
    entries: list[dict[str, Any]] = [
        entry for entry in (raw_entries or []) if entry
    ]

    _console.print(f"[bold yellow]➜ Playlist contains {len(entries)} videos[/bold yellow]")

    playlist_info["entries"] = entries
    return playlist_info

def download_playlist(playlist_info: dict[str, Any],
                      db_manager: DatabaseManager,
                      console: Optional[RichConsole] = None) -> None:
    """
    Download playlist as audio files and convert to .ogg file.

    Args:
        playlist_info (dict): Playlist object
        db_manager: DatabaseManager instance
    """
    _console = console if console else RichConsole()

    for idx, entry in enumerate(playlist_info["entries"], start=1):
        video_id = entry["id"]
        channel_name = entry.get("uploader")
        channel_handle = entry.get("uploader_id")
        title = string_utils.clean_title(entry["title"])
        
        if channel_name and "러끼" in channel_name:
            title = string_utils.special_processing_7ucky(title)
        
        if not channel_name: # Private videos
            continue
        
        filename = f"{string_utils.clean_filename(title)} ({video_id}).webm"
        filepath = os.path.join(config.DOWN_DIR, string_utils.clean_channel_name(channel_name), filename)

        _console.print(f"\n[bold green]⬇ Downloading {title} ({video_id}) ({idx}/{len(playlist_info["entries"])})[/bold green]")

        if db_manager.is_downloaded(video_id):
            _console.print(f"    [dim]⏭ Skipping download:[/dim] {title} ({video_id})")
            continue

        try:
            download_video(filepath=filepath,
                            video_url=entry["url"],
                            channel_name=channel_name,
                            trial_count=3,
                            console=_console)
        except DownloadError:
            _console.print(f"    [dim]⏭ Skipping download:[/dim] {title} ({video_id})")
            continue

        new_filepath = ""

        # Try 3 times before failing
        trial_count = 10
        for trial in range(0, trial_count):
            try:
                new_filepath = convert.convert_to_ogg(filepath)
            except FileConversionError as e:
                _console.print(f"    🔄 Retrying... ({trial+1}/{trial_count-1})")
                _console.print(f"    [dim]⏭ Skipping conversion:[/dim] {title} ({video_id})")
            else:
                break
        
        if new_filepath == "":
            raise ConversionMaxRetryAttemptError(f"Conversion failed: Max retry attempts reached. (tried {trial_count-1} times.)")

        filename = os.path.basename(new_filepath)
        metadata.update_metadata(new_filepath, title, video_id, channel_name, channel_handle, db_manager)
        db_manager.save_video_info(video_id, title, channel_name, channel_handle, filename)

def download_video(filepath: str,
                   video_url: str,
                   channel_name: str,
                   trial_count: int,
                   console: Optional[RichConsole] = None) -> None:
    """
    Downloads a video with retry logic and returns its metadata.

    This function attempts to download a video from the given URL to `filepath`.
    It includes a retry mechanism for robustness and handles directory creation.

    Args:
        filepath (str): Full path to save the video, including filename and extension.
        video_url (str): The URL of the video to download.
        channel_name (str): Channel name, used for organizing the download directory.
        trial_count (int): Maximum number of download attempts.
        console (Optional[RichConsole]): `rich.console.Console` object for styled output.

    Raises:
        DownloadError: If download fails after all specified retries. Contains original
                       Exception object in original_exception.
    """
    _console = console if console else RichConsole()

    success = False
    original_exception = None

    for trial in range(0, trial_count+1):
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.join(config.DOWN_DIR, string_utils.clean_channel_name(channel_name)), exist_ok=True)

            # Delete target file if exists
            if os.path.exists(filepath):
                os.remove(filepath)

            # Download video
            with yt_dlp.YoutubeDL({
                "format": "bestaudio[ext=webm]/best",
                "outtmpl": filepath,
                "noplaylist": True,
                "quiet": True,
                "writedescription": False,
                "writeinfojson": False,
                "extract_flat": False,
                "extract_thumbnail": False,
            }) as ydl:
                video_info = ydl.extract_info(video_url) # type: ignore
                _console.print(f"    [bold cyan]✔ Downloaded:[/bold cyan] {video_info.get('title')} ({video_info.get('id')})") # type: ignore
        except Exception as e:
            original_exception = e
            _console.print(f"    [red]✖ Error:[/red] {e}")
            _console.print(f"    🔄 Retrying... ({trial+1}/{trial_count-1})")
        else:
            success = True
            break
    
    if not success:
        raise DownloadError(
            f"Download failed: Max retry attempts reached. (tried {trial_count-1} times.)",
            reason="Download retrial reached max retrial count",
            original_exception=original_exception
        )