#!/usr/bin/env python3

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from automarketing.mcp_contract_validator import validate_mcp_contract


def parse_headers(values: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid header `{value}`. Use KEY=VALUE.")
        key, header_value = value.split("=", 1)
        headers[key] = header_value
    return headers


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a portfolio application's MCP contract."
    )
    parser.add_argument("endpoint_url", help="Streamable HTTP MCP endpoint URL")
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        help="HTTP header in KEY=VALUE form. May be passed multiple times.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the validation report as JSON.",
    )
    args = parser.parse_args()

    try:
        headers = parse_headers(args.header)
        report = asyncio.run(validate_mcp_contract(args.endpoint_url, headers=headers))
    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(report.to_text())

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

