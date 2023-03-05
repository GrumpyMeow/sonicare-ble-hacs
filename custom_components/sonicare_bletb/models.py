"""The Sonicare ble toothbrush integration models."""
from __future__ import annotations

from dataclasses import dataclass

from sonicare_bletb import SonicareBLETB

from .coordinator import SonicareBLETBCoordinator


@dataclass
class SonicareBLETBData:
    """Data for the Sonicare ble toothbrush integration."""

    title: str
    device: SonicareBLETB
    coordinator: SonicareBLETBCoordinator
