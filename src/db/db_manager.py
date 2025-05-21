import sqlite3
from typing import Optional, Dict

from rich.console import Console as RichConsole

import src.config as config

class DatabaseManager:
    """
    Manages all database operations for video and channel profile information.
    """

    def __init__(self, console: Optional[RichConsole] = None) -> None:
        """
        Initializes the DatabaseManager with the path to the SQLite database.

        Args:
            db_path (str): The file path to the SQLite database.
        """
        self._console = console if console else RichConsole()
        self.db_path = config.DB_PATH
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Establishes and returns a database connection.
        Sets row_factory to sqlite3.Row for column name access.

        Returns:
            sqlite3.Connection: An active SQLite database connection.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Allow accessing columns by name (e.g., row["title"])
        return conn

    def _initialize_db(self) -> None:
        """
        Initializes the database by creating necessary tables if they don't exist.
        This is called automatically when a DatabaseManager instance is created.
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    title TEXT,
                    channel_name TEXT,
                    channel_handle TEXT,
                    filename TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS channel_profiles (
                    channel_handle TEXT PRIMARY KEY,
                    image_filename TEXT
                )
                """
            )
            conn.commit()
        self._console.print("[bold green]✔ Database initialized.[/bold green]")

    def is_downloaded(self, video_id: str) -> bool:
        """
        Checks if a video_id is registered in the DB.

        Args:
            video_id (str): Video ID to lookup.

        Returns:
            bool: True if the video_id is registered in the DB, False otherwise.
        """
        with self._get_connection() as conn:
            # SELECT 1 is efficient for quickly checking existence
            result = conn.execute("SELECT 1 FROM videos WHERE video_id=?", (video_id,)).fetchone()
            return result is not None

    def save_video_info(self,
                        video_id: str,
                        title: str,
                        channel_name: str,
                        channel_handle: str,
                        filename: str) -> None:
        """
        Inserts information of a downloaded video into the DB.

        Args:
            video_id (str): Video ID.
            title (str): Video title.
            channel_name (str): Channel name.
            channel_handle (str): Channel handle.
            filename (str): Downloaded file name.
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO videos (video_id, title, channel_name, channel_handle, filename) VALUES (?, ?, ?, ?, ?)",
                (video_id, title, channel_name, channel_handle, filename)
            )
            conn.commit()
        self._console.print(f"    [bold cyan]✔ Saved to DB:[/bold cyan] {title} ({video_id})")

    def get_video_info(self, video_id: str) -> Optional[Dict[str, str]]:
        """
        Retrieves video information (title, channel_name, filename) from the DB.

        Args:
            video_id (str): Video ID to lookup.

        Returns:
            Optional[Dict[str, str]]: Video details (title, channel_name, filename)
                                      or None if not found.
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT title, channel_name, filename FROM videos WHERE video_id=?",
                (video_id,)
            ).fetchone()

            if row:
                return {
                    "title": row["title"],
                    "channel_name": row["channel_name"],
                    "filename": row["filename"]
                }
            else:
                return None

    def save_channel_image_filename(self, channel_handle: str, image_filename: str) -> None:
        """
        Inserts or updates a channel's profile image path in the DB.

        Args:
            channel_handle (str): Channel handle to insert or update.
            image_filename (str): The file path to the channel's profile image.
        """
        with self._get_connection() as conn:
            # Use INSERT OR REPLACE to update if existing, insert if not.
            conn.execute(
                "INSERT OR REPLACE INTO channel_profiles (channel_handle, image_filename) VALUES (?, ?)",
                (channel_handle, image_filename)
            )
            conn.commit()
        self._console.print(f"    [bold cyan]✔ Saved channel profile for:[/bold cyan] {channel_handle}")

    def get_channel_image_filename(self, channel_handle: str) -> Optional[str]:
        """
        Retrieves profile image filename from the DB for a given channel handle.

        Args:
            channel_handle (str): Channel handle to lookup.

        Returns:
            Optional[str]: Image filename or None if not found.
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT image_filename FROM channel_profiles WHERE channel_handle=?",
                (channel_handle,)
            ).fetchone()

            if row:
                return row["image_filename"]
            else:
                return None
