from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SendMode(str, Enum):
    DRY_RUN = "dry_run"
    ARMED_PAPER = "armed_paper"
    ARMED_LIVE = "armed_live"


class SendModeConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class SendModeResolution:
    send_mode: SendMode
    action_mode: str
    dry_run: bool
    paper_send_armed: bool
    live_send_armed: bool


_RESOLUTIONS: dict[SendMode, SendModeResolution] = {
    SendMode.DRY_RUN: SendModeResolution(
        send_mode=SendMode.DRY_RUN,
        action_mode="dry_run",
        dry_run=True,
        paper_send_armed=False,
        live_send_armed=False,
    ),
    SendMode.ARMED_PAPER: SendModeResolution(
        send_mode=SendMode.ARMED_PAPER,
        action_mode="paper_send",
        dry_run=False,
        paper_send_armed=True,
        live_send_armed=True,
    ),
    SendMode.ARMED_LIVE: SendModeResolution(
        send_mode=SendMode.ARMED_LIVE,
        action_mode="live_send",
        dry_run=False,
        paper_send_armed=False,
        live_send_armed=True,
    ),
}


def _coerce_send_mode(send_mode: SendMode | str) -> SendMode:
    if isinstance(send_mode, SendMode):
        return send_mode
    try:
        return SendMode(str(send_mode).strip())
    except ValueError as exc:
        valid = ", ".join(mode.value for mode in SendMode)
        raise SendModeConfigurationError(f"unknown send_mode={send_mode!r}; expected one of: {valid}") from exc


def resolve_send_mode(
    send_mode: SendMode | str | None = None,
    *,
    dry_run: bool | None = None,
    arm_paper_send: bool | None = None,
    live_send_armed: bool | None = None,
) -> SendModeResolution:
    resolved_mode: SendMode
    if send_mode is not None:
        resolved_mode = _coerce_send_mode(send_mode)
    elif arm_paper_send is True:
        resolved_mode = SendMode.ARMED_PAPER
    elif arm_paper_send is False:
        resolved_mode = SendMode.DRY_RUN
    elif dry_run is True:
        resolved_mode = SendMode.DRY_RUN
    elif dry_run is False and live_send_armed is True:
        resolved_mode = SendMode.ARMED_LIVE
    elif live_send_armed is True:
        resolved_mode = SendMode.ARMED_LIVE
    else:
        resolved_mode = SendMode.DRY_RUN

    resolution = _RESOLUTIONS[resolved_mode]
    mismatches: list[str] = []
    if dry_run is not None and dry_run is not resolution.dry_run:
        mismatches.append(f"dry_run={dry_run!r}")
    if arm_paper_send is not None and arm_paper_send is not resolution.paper_send_armed:
        mismatches.append(f"arm_paper_send={arm_paper_send!r}")
    if live_send_armed is not None and live_send_armed is not resolution.live_send_armed:
        mismatches.append(f"live_send_armed={live_send_armed!r}")
    if mismatches:
        raise SendModeConfigurationError(
            f"illegal send mode flags for {resolution.send_mode.value}: {', '.join(mismatches)}"
        )
    return resolution


__all__ = [
    "SendMode",
    "SendModeConfigurationError",
    "SendModeResolution",
    "resolve_send_mode",
]
