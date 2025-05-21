from typing import Optional

def mime_to_extension(mime_type: Optional[str]) -> Optional[str]:
    """
    Converts a MIME type to a common file extension.

    Args:
        mime_type (str): The MIME type string (e.g., "image/jpeg").

    Returns:
        Optional[str]: The corresponding file extension (e.g., ".jpg") or None if not found.
    """
    if mime_type == "image/png":
        return "png"
    elif mime_type == "image/jpeg":
        return "jpg"
    elif mime_type == "image/gif":
        return "gif"
    elif mime_type == "image/webp":
        return "webp"
    # Add more MIME type mappings as needed
    return None