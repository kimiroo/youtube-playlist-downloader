import os
from typing import Optional

from rich.console import Console

import src.config as config
import src.downloader.download_playlist as download_playlist
import src.playlist.smpl as smpl
from src.db.db_manager import DatabaseManager

class Application:
    """
    Main application class that orchestrates various components.
    """
    def __init__(self):
        self.console = Console()
        self.db_manager = DatabaseManager()

        # Ensure directories exist
        os.makedirs(config.SMPL_DIR, exist_ok=True)
        os.makedirs(config.ICON_DIR, exist_ok=True)

        self.console.print("[bold green]✔ Application initialized.[/bold green]")

    def run(self,
            playlist_url: str,
            playlist_name: Optional[str],
            reverse: bool) -> None:
        """
        Main entry point for the application's core logic.

        Args:
            playlist_url (str): Target YouTube playlist URL
            playlist_name (Optional[str]): Custom playlist name
            reverse (bool): Generate SMPL playlist in reverse order.
        """

        # Fetch playlist information
        playlist_info = download_playlist.get_playlist_info(playlist_url)
        final_playlist_name = ""

        self.console.print(f"[bold blue]➜ Reversed:[/bold blue] {reverse}")
        if playlist_name:
            final_playlist_name = playlist_name
            self.console.print(f"[bold blue]➜ Custom Playlist Name:[/bold blue] {playlist_name}")
        else:
            final_playlist_name = playlist_info['title']
            self.console.print(f"[bold blue] Playlist Name:[/bold blue] {playlist_name}")

        new_playlist_info = download_playlist.download_playlist(playlist_info, self.db_manager)
        smpl.generate_smpl(new_playlist_info, final_playlist_name, self.db_manager, reverse)
        self.console.print("[bold green]✔ All done![/bold green]")