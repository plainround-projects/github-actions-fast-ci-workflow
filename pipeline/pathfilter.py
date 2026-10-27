"""Model of GitHub's ``paths`` and ``paths-ignore`` filters: does a push that changed these files start a workflow?

Pattern syntax (from the workflow syntax reference): ``*`` matches any characters except ``/``, ``**`` matches any
characters including ``/``, ``?`` makes the preceding character optional, ``+`` repeats it, ``[...]`` is a class.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate one filter pattern into an anchored regular expression."""
    out: list[str] = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if char == "*":
            out.append("[^/]*")
        elif char in "?+":
            out.append(char)
        elif char == "[":
            end = pattern.index("]", i)
            out.append(pattern[i : end + 1])
            i = end
        else:
            out.append(re.escape(char))
        i += 1
    return re.compile("".join(out))


def matches(path: str, patterns: Iterable[str]) -> bool:
    """Return whether ``path`` matches any of ``patterns``."""
    return any(glob_to_regex(pattern).fullmatch(path) for pattern in patterns)


def starts_workflow(changed: Sequence[str], *, paths: Sequence[str] = (), paths_ignore: Sequence[str] = ()) -> bool:
    """Return whether a push that changed ``changed`` starts a workflow with these filters.

    With ``paths`` the workflow starts when any changed file matches; with ``paths-ignore`` it starts unless every
    changed file matches. GitHub does not allow both on one event.
    """
    if paths and paths_ignore:
        raise ValueError("paths and paths-ignore cannot be used together on one event")
    if paths:
        return any(matches(path, paths) for path in changed)
    if paths_ignore:
        return not all(matches(path, paths_ignore) for path in changed)
    return True
