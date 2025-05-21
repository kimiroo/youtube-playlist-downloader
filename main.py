import argparse

from rich.prompt import Prompt

from src.app import Application

def main():
    app = Application()

    parser = argparse.ArgumentParser(description="Download YouTube playlist audio and generate SMPL playlist.")
    parser.add_argument("playlist_url", nargs="?", help="YouTube playlist URL (optional, for CLI mode)")
    parser.add_argument("-n", "--playlist_name", help="Custom playlist name (optional)")
    parser.add_argument("-r", "--reverse", action="store_true", help="Reverse playlist order")

    args = parser.parse_args()

    playlist_url = ""
    playlist_name = ""
    reverse_order = False

    if args.playlist_url:
        # Command-line mode
        playlist_url = args.playlist_url
        playlist_name = args.playlist_name
        reverse_order = args.reverse or False

    else:
        # Manual mode
        playlist_url = Prompt.ask("[bold yellow]Enter YouTube playlist URL[/bold yellow]")
        playlist_name = Prompt.ask("[bold yellow]Enter custom playlist name (optional)[/bold yellow]", default=None)
        reverse_order = Prompt.ask("[bold yellow]Reverse playlist order? (yes/no)[/bold yellow]", default="no").lower() == "yes"
    
    app.run(
        playlist_url=playlist_url,
        playlist_name=playlist_name,
        reverse=reverse_order
    )

if __name__ == "__main__":
    main()