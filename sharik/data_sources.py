from .abstract import DataSource, ContentSupplier
from dataclasses import dataclass
from typing import Tuple, Iterable, Generator
from os import walk
from os.path import isfile, isdir, join
from functools import partial

def _id(x):
    return x

@dataclass
class InlineDataSource(DataSource):
    _collection_of_files: Tuple[Tuple[str, bytes]]

    def provide_files(self) -> Iterable[Tuple[str, ContentSupplier]]:
        return tuple((file_name, partial(_id, buffer))
                    for (file_name, buffer) in self._collection_of_files)

def _gen_files(starting_path) -> Generator[str, None, None]:
    if isfile(starting_path):
        yield isfile

    elif isdir(starting_path):
        for(dir_path, dirnames, file_names) in walk(starting_path):
            yield from (join(dir_path, file_name) for file_name in file_names)

    else:
        raise ValueError(f"Unknown or invalid path {starting_path}")

def _read_file(file_name: str) -> bytes:
    with open(file_name, 'rb') as file_object:
        return file_object.read()

@dataclass
class FileDataSource(DataSource):
    _scan_root: str

    def provide_files(self) -> Iterable[Tuple[str, ContentSupplier]]:
        return tuple(
            (file_name, partial(_read_file, file_name))
            for file_name in _gen_files(self._scan_root)
        )