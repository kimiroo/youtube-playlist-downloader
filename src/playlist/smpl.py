import os
import json
from typing import Any, Optional

from rich.console import Console as RichConsole

import src.config as config
import src.util.string_utils as string_utils
from src.db.db_manager import DatabaseManager


def generate_smpl(playlist_info: dict[str, Any],
                  playlist_name: str,
                  db_manager: DatabaseManager,
                  reverse: bool = False,
                  console: Optional[RichConsole] = None):
    """
    Generates an SMPL playlist file for a YouTube playlist.

    This function processes video info, checks download status via `db_manager`,
    and creates an SMPL playlist file with local audio paths.
    Playlist order can be reversed.

    Args:
        playlist_info (dict[str, Any]): YouTube playlist details from yt-dlp.
        playlist_name (str): Desired name for the .m3u playlist file.
        db_manager (DatabaseManager): DB manager to check downloaded video info.
        reverse (bool): If True, playlist entries are reversed (newest first). Defaults to False.
        console (Optional[RichConsole]): `rich.console.Console` for styled output.

    Returns:
        None: Generates a file; does not return a value.
    """
    _console = console if console else RichConsole()
                  
    videos: list[dict[str, Any]] = []
    for entry in playlist_info["entries"]:
        if not entry:
            continue
        video_id = entry["id"]
        db_info = db_manager.get_video_info(video_id)
        
        if db_info:
            is_video_exist = os.path.exists(os.path.join(config.DOWN_DIR,
                                                         string_utils.clean_channel_name(db_info['channel_name']),
                                                         db_info['filename']))
            if is_video_exist:
                videos.append({
                    "artist": db_info["channel_name"],
                    "info": f"{config.SMPL_PREFIX}{string_utils.clean_channel_name(db_info['channel_name'])}/{db_info['filename']}",
                    "order": len(videos) if not reverse else 0,
                    "title": playlist_name if playlist_name else db_info["title"],
                    "type": 65537
                })

    if reverse:
        videos.reverse()
        for i, video in enumerate(videos):
            video["order"] = i

    smpl_data: dict[str, Any] = {
        "members": videos,
        "name": playlist_name,
        "recentlyPlayedDate": 0,
        "sortBy": 4,
        "version": 1
    }

    smpl_path = os.path.join(config.SMPL_DIR, f"{string_utils.clean_filename(playlist_name)}.smpl")
    with open(smpl_path, "w", encoding="utf-8") as f:
        json.dump(smpl_data, f, ensure_ascii=False, separators=(",", ":"))

    _console.print(f"[bold green]✔ SMPL saved:[/bold green] {smpl_path}")