"""Upload a bot zip and/or enroll an existing bot in a competition on aiarena.net.

Usage:
    AIARENA_API_TOKEN=... python scripts/upload_to_aiarena.py --bot-id 772
    AIARENA_API_TOKEN=... python scripts/upload_to_aiarena.py \
        --bot phoenix --bot-id 772 --competition-id 38
    AIARENA_API_TOKEN=... python scripts/upload_to_aiarena.py \
        --bot-id 772 --competition-id 38 --enroll-only
    AIARENA_API_TOKEN=... python scripts/upload_to_aiarena.py \
        --bot griffin --bot-id 5678

The bot must already exist on aiarena.net (create it once via the website:
Profile -> Bots -> Create Bot, type "python"; race Protoss/plays P for
phoenix, race Terran/plays T for griffin).
Get the API token from https://aiarena.net/profile/token/.
"""

import argparse
import base64
import sys
from os import environ
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent

# dir name -> (ladder bot name, wiki blurb)
BOT_REGISTRY = {
    "phoenix": ("PhoenixBot", "# PhoenixBot\n\nProtoss bot made with "
                "[ares-sc2](https://github.com/AresSC2/ares-sc2)."),
    "griffin": ("GriffinBot", "# GriffinBot\n\nTerran bot made with "
                "[ares-sc2](https://github.com/AresSC2/ares-sc2)."),
}

ENROLL_MUTATION = """
mutation UpdateCompetitionParticipation($input: UpdateCompetitionParticipationInput!) {
  updateCompetitionParticipation(input: $input) {
    errors {
      field
      messages
    }
  }
}
"""


def _global_id(type_name: str, db_id: str | int) -> str:
    return base64.b64encode(f"{type_name}:{db_id}".encode()).decode()


def upload_zip(token: str, bot_id: str, zip_path: Path, wiki: str) -> None:
    if not zip_path.is_file():
        sys.exit(f"{zip_path} not found - run scripts/create_ladder_zip.py first")

    url = f"https://aiarena.net/api/bots/{bot_id}/"
    with open(zip_path, "rb") as bot_zip:
        response = requests.patch(
            url,
            headers={"Authorization": f"Token {token}"},
            data={
                "bot_zip_publicly_downloadable": False,
                "bot_data_publicly_downloadable": False,
                "bot_data_enabled": True,
                "wiki_article_content": wiki,
            },
            files={"bot_zip": bot_zip},
            timeout=120,
        )
    print(response.status_code)
    print(response.content[:1000])
    if response.status_code >= 300:
        sys.exit(1)
    print("Upload OK")


def enroll_in_competition(token: str, bot_id: str, competition_id: int) -> None:
    response = requests.post(
        "https://aiarena.net/graphql/",
        headers={"Authorization": f"Token {token}"},
        json={
            "query": ENROLL_MUTATION,
            "variables": {
                "input": {
                    "bot": _global_id("BotType", bot_id),
                    "competition": _global_id("CompetitionType", competition_id),
                    "active": True,
                }
            },
        },
        timeout=30,
    )
    print(response.status_code)
    print(response.text[:1000])
    if response.status_code >= 300:
        sys.exit(1)

    payload = response.json()
    if payload.get("errors"):
        sys.exit(f"GraphQL errors: {payload['errors']}")
    result = (payload.get("data") or {}).get("updateCompetitionParticipation") or {}
    if result.get("errors"):
        sys.exit(f"Enrollment errors: {result['errors']}")
    print(f"Enroll OK (bot {bot_id} -> competition {competition_id})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bot", default="phoenix", choices=sorted(BOT_REGISTRY),
                        help="which repo bot to upload")
    parser.add_argument("--bot-id", required=True)
    parser.add_argument("--zip", default=None,
                        help="default: <BotName>.zip in the repo root")
    parser.add_argument("--wiki", default=None)
    parser.add_argument("--competition-id", type=int, default=None,
                        help="also enroll/activate the bot in this competition ID (e.g. 38 for 2026 Season 2)")
    parser.add_argument("--enroll-only", action="store_true",
                        help="skip uploading a zip and only enroll in --competition-id")
    args = parser.parse_args()

    if args.enroll_only and args.competition_id is None:
        sys.exit("--enroll-only requires --competition-id")

    bot_name, default_wiki = BOT_REGISTRY[args.bot]
    args.zip = args.zip or str(REPO_ROOT / f"{bot_name}.zip")
    args.wiki = args.wiki or default_wiki

    token = environ.get("AIARENA_API_TOKEN")
    if not token:
        sys.exit("Set AIARENA_API_TOKEN (from https://aiarena.net/profile/token/)")

    if not args.enroll_only:
        upload_zip(token, args.bot_id, Path(args.zip), args.wiki)

    if args.competition_id is not None:
        enroll_in_competition(token, args.bot_id, args.competition_id)


if __name__ == "__main__":
    main()
