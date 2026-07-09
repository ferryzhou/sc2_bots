"""Upload PhoenixBot.zip to an existing bot on aiarena.net.

Usage:
    AIARENA_API_TOKEN=... python scripts/upload_to_aiarena.py --bot-id 1234

The bot must already exist on aiarena.net (create it once via the website:
Profile -> Bots -> Create Bot, type "python", race Protoss, plays race P).
Get the API token from https://aiarena.net/profile/token/.
"""

import argparse
import sys
from os import environ
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = REPO_ROOT / "PhoenixBot.zip"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bot-id", required=True)
    parser.add_argument("--zip", default=str(ZIP_PATH))
    parser.add_argument("--wiki", default="# PhoenixBot\n\nProtoss bot made with "
                        "[ares-sc2](https://github.com/AresSC2/ares-sc2).")
    args = parser.parse_args()

    token = environ.get("AIARENA_API_TOKEN")
    if not token:
        sys.exit("Set AIARENA_API_TOKEN (from https://aiarena.net/profile/token/)")

    zip_path = Path(args.zip)
    if not zip_path.is_file():
        sys.exit(f"{zip_path} not found - run scripts/create_ladder_zip.py first")

    url = f"https://aiarena.net/api/bots/{args.bot_id}/"
    with open(zip_path, "rb") as bot_zip:
        response = requests.patch(
            url,
            headers={"Authorization": f"Token {token}"},
            data={
                "bot_zip_publicly_downloadable": False,
                "bot_data_publicly_downloadable": False,
                "bot_data_enabled": True,
                "wiki_article_content": args.wiki,
            },
            files={"bot_zip": bot_zip},
        )
    print(response.status_code)
    print(response.content[:1000])
    if response.status_code >= 300:
        sys.exit(1)
    print("Upload OK")


if __name__ == "__main__":
    main()
