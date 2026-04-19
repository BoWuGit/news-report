"""CDP Browser adapter — re-exports from ``social_timeline_runtime``.

The canonical implementation now lives in the ``social_timeline_runtime``
package.  This module re-exports the public API so existing ``news_report``
consumers continue to work without changes.
"""

from social_timeline_runtime.normalize import (  # noqa: F401
    JIKE_EXTRACTION_SCRIPT,
    X_EXTRACTION_SCRIPT,
    normalize_jike_posts,
    normalize_x_posts,
)
