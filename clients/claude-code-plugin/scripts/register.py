#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _su_lib import api_post, save_and_print


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a Sprint Undertaker account")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--character-name", required=True)
    parser.add_argument("--code", help="Email verification code (omit to only send the code)")
    parser.add_argument("--server-url", default="http://localhost:8000")
    args = parser.parse_args()

    base_url = args.server_url.rstrip("/")

    if args.code is None:
        print(f"Registering {args.email} (character: {args.character_name}) ...")
        result = api_post(
            base_url,
            "/api/auth/register",
            {"email": args.email, "password": args.password, "character_name": args.character_name},
        )
        print(result.get("message", "Verification code sent."))
        return 0

    print(f"Verifying {args.email} ...")
    auth = api_post(
        base_url,
        "/api/auth/verify-email",
        {"email": args.email, "code": args.code},
    )
    save_and_print(base_url, auth["access_token"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
