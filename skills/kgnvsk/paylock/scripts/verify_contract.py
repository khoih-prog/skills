#!/usr/bin/env python3
from __future__ import annotations

import argparse

from paylock_api import PayLockClient, print_json, run_with_error_handling


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify delivery for a PayLock contract")
    parser.add_argument("--id", required=True, help="Contract ID")
    parser.add_argument("--payer-token", required=True, help="Payer secret token")
    parser.add_argument("--api", default=None, help="Override API base URL")
    args = parser.parse_args()

    client = PayLockClient(base_url=args.api)
    payload = {"payer_token": args.payer_token}
    print_json(client.request("POST", f"/{args.id}/verify", payload=payload))


if __name__ == "__main__":
    run_with_error_handling(main)
