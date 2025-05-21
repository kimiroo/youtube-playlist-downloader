import os
import base64
from typing import Optional

from mutagen.flac import Picture
from mutagen.oggopus import OggOpus
from rich.console import Console as RichConsole

import src.config as config
import src.downloader.channel as channel
from src.db.db_manager import DatabaseManager

def update_metadata(filepath: str,
                    title: str,
                    video_id: str,
                    channel_name: str,
                    channel_handle: str,
                    db_manager: DatabaseManager,
                    console: Optional[RichConsole] = None) -> None:
    """
    Update metadata of given .ogg file.

    Args:
        filepath (str): Path to taget .ogg file.
        title (str): Video title.
        video_id (str): Video ID.
        channel_name (str): Channel name.
        channel_handle (str): Channel handle.
        db_manager (DatabaseManager): DatabaseManager instance.
    """
    _console = console if console else RichConsole()
    
    # Get channel profile picture
    image_filename = db_manager.get_channel_image_filename(channel_handle)
    image_path = None
    if image_filename:
        image_path = os.path.join(config.ICON_DIR, image_filename)
    else:
        profile_image_url = channel.get_channel_profile_url(channel_handle)
        if profile_image_url:
            image_path = channel.download_channel_profile_image(channel_handle=channel_handle,
                                                                url=profile_image_url,
                                                                db_manager=db_manager)
    
    # Open file and put text metadata
    ogg = OggOpus(filepath)
    ogg["title"] = title
    ogg["artist"] = channel_name
    ogg["comment"] = f"https://www.youtube.com/watch?v={video_id}"

    # Put album art if exists
    if image_path:
        try:
            # Read the image data
            with open(image_path, "rb") as img:
                image_data = img.read()

            if image_path.lower().endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            elif image_path.lower().endswith(".png"):
                mime = "image/png"
            else:
                raise ValueError("Unsupported image format. Please use JPEG or PNG.")

            # Create a Picture object
            picture = Picture()
            picture.mime = mime
            picture.type = 3  # Front cover
            picture.data = image_data

            # Convert to Base64 and add to Vorbis comments
            encoded_picture = base64.b64encode(picture.write()).decode("utf-8")
            ogg["METADATA_BLOCK_PICTURE"] = [encoded_picture]
        except Exception as image_error:
            _console.print(f"    ⚠ Image processing error: {image_error}")

    # Save the updated metadata
    ogg.save() # type: ignore