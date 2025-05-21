from typing import Optional

class YPDError(Exception):
    """Youtube-Playlist-Downloader Exception."""
    pass

class DownloadError(YPDError):
    """Error while downloading."""
    def __init__(self,
                 message: str = "Error occured while downloading.",
                 reason: Optional[str] = None,
                 original_exception: Optional[Exception] = None) -> None:
        super().__init__(f"{message}: {original_exception}" if original_exception else message)
        self.reason = reason
        self.original_exception = original_exception

class ChannelError(YPDError):
    """Error while processing channel data."""
    def __init__(self,
                 message: str = "Error occured while processing channel data.",
                 reason: Optional[str] = None) -> None:
        super().__init__(message)
        self.reason = reason

class ProfileImageDownloadError(ChannelError):
    """Error while downloading channel profile image."""
    def __init__(self,
                 url: str,
                 original_exception: Exception,
                 message: str = "Error occured while downloading channel profile image.",
                 reason: Optional[str] = "Profile image download error") -> None:
        super().__init__(f"{message}: {original_exception}")
        self.reason = reason
        self.url = url
        self.original_exception = original_exception

class NoProfileImageError(ChannelError):
    """Channel profile image URL not found."""
    def __init__(self,
                 channel_handle: str,
                 message: str = "Channel profile image URL not found.",
                 reason: str = "No profile image error") -> None:
        super().__init__(message)
        self.channel_handle = channel_handle
        self.reason = reason

class GetProfileImageURLError(ChannelError):
    """Error while finding URL of channel profile image."""
    def __init__(self,
                 channel_handle: str,
                 original_exception: Exception,
                 message: str = "Error occured while finding URL of channel profile image.",
                 reason: str = "Get profile image URL error") -> None:
        super().__init__(f"{message}: {original_exception}")
        self.channel_handle = channel_handle
        self.reason = reason
        self.original_exception = original_exception

class ConvertError(YPDError):
    """Error while converting."""
    def __init__(self,
                 message: str = "Error occured while converting.",
                 reason: Optional[str] = None) -> None:
        super().__init__(message)
        self.reason = reason

class FileConversionError(ConvertError):
    """Error while converting file."""
    def __init__(self,
                 input_path: Optional[str],
                 output_path: Optional[str],
                 original_exception: Exception,
                 message: str = "Error occured while converting.",
                 reason: str = "File conversion error") -> None:
        super().__init__(f"""{message}: {original_exception}
                             input path: {input_path}
                             output path: {output_path}""")
        self.reason = reason
        self.input_path = input_path
        self.output_path = output_path
        self.original_exception = original_exception

class ConversionMaxRetryAttemptError(ConvertError):
    """Conversion retrial reached max retrial count."""
    def __init__(self,
                 message: str = "Conversion retrial reached max retrial count.") -> None:
        super().__init__(message)

class UnsupportedFileTypeError(YPDError):
    """Unsupported file type"""
    def __init__(self, file_type: Optional[str], message: str = "Unsupported file type") -> None:
        super().__init__(f"{message}: {file_type}")
        self.file_type = file_type

class PlaylistError(YPDError):
    """Error while processing playlist."""
    def __init__(self,
                 message: str = "Error occured while processing playlist.",
                 reason: Optional[str] = None) -> None:
        super().__init__(message)
        self.reason = reason
