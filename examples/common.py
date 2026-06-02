"""Shared helpers for running ATK Connect examples."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

SDK_ROOT = Path(__file__).resolve().parents[1]
if str(SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(SDK_ROOT))

from atk_python_sdk import atkClose, atkConnect, atkOpen, detect_ok

DEFAULT_BASE_URL = "http://localhost:8080"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 6655
DEFAULT_WAIT_MS = 10
LONG_COMMAND_WAIT_MS = 1000
ATK_HOME = os.environ.get("ATK_HOME", "/opt/ATK/ATK-4.0.0")


@dataclass(frozen=True)
class ConnectCommand:
    """One ATK Connect command from an example."""

    command: str
    param: str
    note: str = ""


@dataclass(frozen=True)
class ConnectExample:
    """Runnable ATK Connect example metadata and command list."""

    key: str
    title: str
    source_doc: str
    commands: tuple[ConnectCommand, ...]
    note: str = ""


class ConnectCommandError(RuntimeError):
    """Raised when an ATK Connect command returns NACK or onError."""


def connect_atk(base_url: str, host: str, port: int) -> None:
    """Connect the Java HTTP bridge to the ATK Connect server."""
    atkOpen(base_url, host, port, 10.0)


def close_atk(base_url: str) -> None:
    """Close the Java HTTP bridge connection to ATK."""
    atkClose(base_url, 5.0)


def without_save(commands: Sequence[ConnectCommand]) -> tuple[ConnectCommand, ...]:
    """Return commands excluding Save commands."""
    return tuple(command for command in commands if command.command != "Save")


def command_wait_ms(command: ConnectCommand) -> int:
    """Use a longer wait for commands that can trigger heavier ATK work."""
    if command.command in {"Astrogator", "Cov", "Cov_RM", "Access", "Access_RM", "Report_RM", "WalkerDelta"}:
        return LONG_COMMAND_WAIT_MS
    return DEFAULT_WAIT_MS


def resolve_param(param: str) -> str:
    """Resolve placeholders used by the original documentation examples."""
    return param.replace("(ATK根目录)", ATK_HOME)


def run_commands(
    base_url: str,
    commands: Iterable[ConnectCommand],
    *,
    example_key: str,
    stop_on_error: bool = True,
) -> bool:
    """Run commands and return True only if every command succeeds."""
    commands_tuple = tuple(commands)
    total = len(commands_tuple)
    all_success = True

    for index, command in enumerate(commands_tuple, start=1):
        note = f"  # {command.note}" if command.note else ""
        param = resolve_param(command.param)
        print(f"[{example_key}] {index}/{total} {command.command} {param}{note}")
        events = atkConnect(
            base_url,
            command.command,
            param,
            wait_ms=command_wait_ms(command),
            timeout_connect=30.0,
        )
        success, reason = detect_ok(events)
        if success:
            continue

        all_success = False
        message = (
            f"案例 {example_key} 第 {index}/{total} 条命令失败："
            f"{command.command} {param}\n"
            f"原因：{reason or '未知错误'}\n"
            f"事件：{events}"
        )
        if stop_on_error:
            raise ConnectCommandError(message)
        print(message)

    return all_success
