from re import compile
from fnmatch import translate
from typing import Iterable, Optional, Pattern

# Supporting both UNIX and Windows directory separators.
# Theoretically, this could cause a false positive for genuine paths
# containing the other OS's separators, but practically this is an
# extremely marginal use case.
_START = r'(^|[/\\])'
_END = r'([/\\]|$)'

def globs_to_pattern(glob_patterns: Iterable[str]) -> Optional[Pattern]:
    if len(glob_patterns) == 0:
        return None
    else:
        return compile(_START +  '|'.join(
            (f'({translate(glob_pattern)})' for glob_pattern in glob_patterns)) + _END)