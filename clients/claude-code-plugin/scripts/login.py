#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _su_lib import api_post, save_and_print


def main() -> int:
    parser = argparse.ArgumentParser(description="Login to Sprint Undertaker")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--server-url", default="http://localhost:8000")
    args = parser.parse_args()

    base_url = args.server_url.rstrip("/")

    print(f"Logging in as {args.email} ...")
    auth = api_post(base_url, "/api/auth/login", {"email": args.email, "password": args.password})
    save_and_print(base_url, auth["access_token"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
