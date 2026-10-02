"""Production personal-definition preparation retains description-only installation evidence."""

from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.adapters.preparation import InstalledWorkflowPreparer, ServiceEndpoints
from slow_thinker_ii.application import library

from ..installations import new_catalog
from ..preparation import PreparationCase
from ..sequence_plans import SCHEMAS


def library_preparer(
    case: PreparationCase, definitions: library.ExperimentLibrary
) -> InstalledWorkflowPreparer:
    installations: InstallationCatalog = new_catalog(case.installed)
    return InstalledWorkflowPreparer(
        definitions,
        installations,
        SCHEMAS,
        case.descriptors,
        lambda: case.configuration,
        case.tariffs,
        case.secrets,
        ServiceEndpoints("http://127.0.0.1:8000/v1"),
        case.directory / "runtime",
        case.adapters,
        case.clock,
    )
