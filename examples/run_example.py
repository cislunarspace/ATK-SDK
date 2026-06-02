#!/usr/bin/env python3
"""Run ATK Connect examples reproduced from atk-doc."""
from __future__ import annotations

import argparse
from typing import Sequence

from common import (
    ConnectCommandError,
    DEFAULT_BASE_URL,
    DEFAULT_HOST,
    DEFAULT_PORT,
    close_atk,
    connect_atk,
    run_commands,
    without_save,
)
from connect_cases import EXAMPLE_BY_KEY, EXAMPLES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ATK Connect examples from ~/codes/atk-doc.")
    parser.add_argument("example", nargs="?", help="Example key to run. Use --list to show keys.")
    parser.add_argument("--list", action="store_true", help="List available examples.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Java HTTP bridge base URL.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="ATK Connect host.")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="ATK Connect port.")
    parser.add_argument("--close", action="store_true", help="Call atkClose after running the example.")
    parser.add_argument("--no-close", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-open", action="store_true", help="Skip atkOpen when the Java bridge is already connected to ATK.")
    parser.add_argument("--no-save", action="store_true", help="Skip Save commands from the reproduced script.")
    parser.add_argument(
        "--max-commands",
        type=int,
        metavar="N",
        help="Run only the first N commands for debugging long examples.",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Continue after NACK/onError and report failures instead of stopping immediately.",
    )
    return parser


def list_examples() -> None:
    for example in EXAMPLES:
        suffix = f" — {example.note}" if example.note else ""
        print(f"{example.key:30} {example.title} ({example.source_doc}){suffix}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        list_examples()
        return 0

    if not args.example:
        parser.error("missing example key; use --list to show available examples")

    example = EXAMPLE_BY_KEY.get(args.example)
    if example is None:
        parser.error(f"unknown example key: {args.example}")

    if args.max_commands is not None and args.max_commands < 1:
        parser.error("--max-commands must be greater than 0")

    commands = without_save(example.commands) if args.no_save else example.commands
    if args.max_commands is not None:
        commands = commands[: args.max_commands]
    print(f"运行案例：{example.key} - {example.title}")
    print(f"来源文档：{example.source_doc}")
    if example.note:
        print(f"说明：{example.note}")

    if not args.no_open:
        connect_atk(args.base_url, args.host, args.port)
    try:
        success = run_commands(
            args.base_url,
            commands,
            example_key=example.key,
            stop_on_error=not args.keep_going,
        )
    except ConnectCommandError as exc:
        print(exc)
        success = False
    finally:
        if args.close:
            close_atk(args.base_url)

    if success:
        print(f"案例 {example.key} 执行完成。")
        return 0

    print(f"案例 {example.key} 执行完成，但存在失败命令。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
