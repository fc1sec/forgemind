"""
Plugin Registry: Central place to register and access reverse state patterns.

Enables ForgeMind to:
1. Discover available patterns by domain
2. Validate that expertise exists for a domain
3. Instantiate patterns on demand
"""

from typing import Optional

from .reverse_state_pattern import ReverseStatePattern


class PluginRegistry:
    """
    Central registry for domain-specific reverse patterns.

    Usage:
        registry = PluginRegistry()
        registry.register(ISO9001ReversePattern)

        if registry.has_pattern("iso9001"):
            pattern = registry.get_pattern("iso9001")
            reversal_plan = pattern.generate_reversal_plan(project, current_state)
    """

    def __init__(self):
        """Initialize empty registry."""
        self._patterns: dict[str, type[ReverseStatePattern]] = {}

    def register(self, pattern_class: type[ReverseStatePattern]) -> None:
        """
        Register a reverse state pattern.

        Args:
            pattern_class: Subclass of ReverseStatePattern

        Raises:
            ValueError: If domain already registered or pattern missing required attrs
        """
        if not hasattr(pattern_class, 'domain'):
            raise ValueError(f"{pattern_class.__name__} missing required 'domain' attribute")

        domain = pattern_class.domain
        if domain in self._patterns:
            raise ValueError(f"Pattern for domain '{domain}' already registered")

        self._patterns[domain] = pattern_class

    def has_pattern(self, domain: str) -> bool:
        """Check if a pattern exists for this domain."""
        return domain in self._patterns

    def get_pattern(self, domain: str) -> Optional[ReverseStatePattern]:
        """
        Get an instance of the pattern for this domain.

        Args:
            domain: Domain string (e.g., "iso9001")

        Returns:
            Instantiated pattern object, or None if not registered
        """
        if domain not in self._patterns:
            return None
        return self._patterns[domain]()

    def get_pattern_class(self, domain: str) -> Optional[type[ReverseStatePattern]]:
        """Return the plugin CLASS for a domain (without instantiating it).

        Use this when you need to instantiate the plugin with constructor
        arguments (e.g. ``ISO9001ReversePattern(variant_id=...)``) that
        ``get_pattern()`` cannot pass through.
        """
        return self._patterns.get(domain)

    def list_supported_domains(self) -> list[str]:
        """Return list of all supported domains."""
        return sorted(self._patterns.keys())

    def get_pattern_metadata(self, domain: str) -> Optional[dict]:
        """Get metadata about a pattern without instantiating it."""
        if domain not in self._patterns:
            return None

        pattern_class = self._patterns[domain]
        return {
            "domain": pattern_class.domain,
            "framework": pattern_class.framework,
            "description": pattern_class.description,
        }

    def list_all_metadata(self) -> list[dict]:
        """Get metadata for all registered patterns."""
        return [
            self.get_pattern_metadata(domain)
            for domain in self.list_supported_domains()
        ]


# Global registry instance (can be imported and used by other modules)
_global_registry = None


def get_plugin_registry() -> PluginRegistry:
    """
    Get or create the global plugin registry.

    Usage:
        registry = get_plugin_registry()
        registry.register(MyPattern)
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
    return _global_registry


def register_builtin_patterns():
    """
    Register all built-in patterns.

    Called during initialization to load default patterns.
    """
    registry = get_plugin_registry()

    # Import here to avoid circular dependencies
    from .ai_ml_pattern import AIMLReversePattern
    from .iso9001_pattern import ISO9001ReversePattern
    from .software_pattern import SoftwareReversePattern

    registry.register(ISO9001ReversePattern)
    registry.register(SoftwareReversePattern)
    registry.register(AIMLReversePattern)
