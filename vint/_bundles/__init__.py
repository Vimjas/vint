from __future__ import absolute_import

try:
    # Try to import system-wide vimlparser module first
    import vimlparser
except ImportError:
    # Fallback to the bundled one if not found
    from . import vimlparser
