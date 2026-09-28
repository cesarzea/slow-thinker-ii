"""Trusted offline preparation and verification of independently installed components."""

from ._descriptions import InstalledDescription
from ._locks import LockedPackage, read_lock
from ._records import ComponentRegistration, ImplementationBase, Resolution
from ._store import InstallationCatalog

__all__ = [
    "InstalledDescription",
    "ComponentRegistration",
    "ImplementationBase",
    "InstallationCatalog",
    "LockedPackage",
    "Resolution",
    "read_lock",
]
