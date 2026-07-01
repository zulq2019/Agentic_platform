"""Metadata Engine — Platform Object framework."""

from aep_meta.domain.models import PlatformObject
from aep_meta.domain.enums import LifecycleState, PrimitiveType
from aep_meta.application.validation import PlatformObjectValidator
from aep_meta.application.platform_object_service import PlatformObjectService

__all__ = [
    "LifecycleState",
    "PlatformObject",
    "PlatformObjectService",
    "PlatformObjectValidator",
    "PrimitiveType",
]

__version__ = "0.1.0"
