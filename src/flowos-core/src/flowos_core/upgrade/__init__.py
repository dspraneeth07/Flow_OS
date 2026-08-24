"""FLOWOS_CORE flow upgrade utilities."""

from flowos_core.upgrade.applier import apply_safe_upgrades
from flowos_core.upgrade.checker import CompatibilityReport, NodeStatus, check_flow_compatibility

__all__ = ["CompatibilityReport", "NodeStatus", "apply_safe_upgrades", "check_flow_compatibility"]
