"""Nautilus-facing CTP instrument provider placeholder."""


class CtpInstrumentProvider:
    """Placeholder for Nautilus instrument loading built on the shared runtime."""

    def __init__(self) -> None:
        self._loaded = False

    @property
    def loaded(self) -> bool:
        return self._loaded
