from .abstract import DataSource, ContentSupplier
from .globs import globs_to_pattern
from pydantic.dataclasses import dataclass
from typing import Tuple, Iterable, Generator, Callable, Pattern, Optional, Sequence
from os import walk, listdir
from os.path import isfile, isdir, join, split, relpath
from functools import partial
from fnmatch import translate


def _id(x):
    return x

@dataclass
class InlineDataSource(DataSource):
    collection_of_files: Sequence[Tuple[str, bytes]]

    def provide_files(self) -> Iterable[Tuple[str, ContentSupplier]]:
        return tuple((file_name, partial(_id, buffer))
                    for (file_name, buffer) in self.collection_of_files)

def _gen_files(starting_path: str, is_recursive: bool) -> Generator[Tuple[str, str], None, None]:
    if isfile(starting_path):
        if is_recursive:
            raise ValueError('Cannot be recursive over a file')
        yield (split(starting_path)[1], starting_path)

    elif isdir(starting_path):
        if is_recursive:
            source = (join(dir_path, file_name)
                      for (dir_path, _ignore, file_names) in walk(starting_path)
                      for file_name in file_names)
        else:
            source = (
                full_path for full_path in 
                (join(starting_path, file_name) for file_name in listdir(starting_path))
                if isfile(full_path))

        for source_path in source:
            archive_path = relpath(source_path, starting_path)
            yield (archive_path, source_path)

    else:
        raise ValueError(f"Unknown or invalid path {starting_path}")

def _read_file(file_name: str) -> bytes:
    with open(file_name, 'rb') as file_object:
        return file_object.read()

@dataclass
class FileDataSource(DataSource):
    scan_root: str
    is_recursive: bool = True
    whitelist_globs: Sequence[str] = ()
    blacklist_globs: Sequence[str] = ()

    def _create_predicate(self) -> Callable[[str], bool]: 
        whitelist_pattern = globs_to_pattern(self.whitelist_globs)
        blacklist_pattern = globs_to_pattern(self.blacklist_globs)
        
        def _predicate(tested: str):
            is_whitelist_match = ((whitelist_pattern is None) or 
                     (whitelist_pattern.search(tested) is not None))
            is_blacklist_non_match = ((blacklist_pattern is None) or
                     (not blacklist_pattern.search(tested)))
            return is_whitelist_match and is_blacklist_non_match

        return _predicate

    def provide_files(self) -> Iterable[Tuple[str, ContentSupplier]]:
        predicate = self._create_predicate()

        return tuple(
            (archive_path, partial(_read_file, full_path))
            for (archive_path, full_path) in _gen_files(self.scan_root, self.is_recursive)
            if predicate(full_path)
        )