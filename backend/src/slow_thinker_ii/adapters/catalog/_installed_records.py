"""Admitted graph data retains both the user definition and effective installed contracts."""

from dataclasses import dataclass

from slow_thinker_ii.adapters.installations import InstalledDescription
from slow_thinker_ii.definitions import SequencePlan


@dataclass(frozen=True)
class TypeInstallation:
    resolution_id: str
    descriptor_json: str


@dataclass(frozen=True)
class ConfiguredInstance:
    instance_id: str
    resolution_id: str
    descriptor_json: str
    description: InstalledDescription


@dataclass(frozen=True)
class InstalledPlan:
    plan: SequencePlan
    configurations: tuple[ConfiguredInstance, ...]
