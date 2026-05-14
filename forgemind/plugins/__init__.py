"""
ForgeMind Plugin System v1.2.0

Enables community experts to contribute domain-specific reverse state machine patterns.
"""

from .plugin_registry import PluginRegistry, get_plugin_registry, register_builtin_patterns
from .reverse_state_pattern import ReverseStatePattern

# Initialize global registry with built-in patterns
register_builtin_patterns()

__all__ = ["ReverseStatePattern", "PluginRegistry", "get_plugin_registry", "register_builtin_patterns"]
