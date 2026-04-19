"""Runtime package for the publishable social timeline skill.

This package is introduced as a monorepo-friendly boundary: the published skill
should call this runtime through a stable CLI instead of importing `news_report`
or reaching into project-local scripts.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
