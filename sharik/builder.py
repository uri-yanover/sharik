from dataclasses import dataclass
from dataclasses import field
from os import path
from typing import Generator, Tuple, List, Iterable, Union
from base64 import b64encode
from zlib import compressobj, MAX_WBITS

from .abstract import DataSource, ContentSupplier
from .globs import globs_to_pattern

# Note that '-' is not a valid base64 character
_END_MARKER_STR = '---END-SHARIK---'
_END_MARKER_BYTES = _END_MARKER_STR.encode('utf-8')
_END_MARKER_CONDITION_BYTES = b'\n' + _END_MARKER_BYTES
_ZLIB_COMPRESSION_LEVEL = 9

# See: https://stackoverflow.com/questions/1838699/how-can-i-decompress-a-gzip-stream-with-zlib
def _compress(data: bytes) -> bytes:
    compress_object = compressobj(level=_ZLIB_COMPRESSION_LEVEL, wbits = MAX_WBITS | 16)
    result = compress_object.compress(data)
    return result + compress_object.flush()

@dataclass
class _SharikShellGenerator(object):
    shell_path: bytes
    final_command: bytes
    trace: bool
    clear_globs: List[str]
    elements: Tuple[Tuple[str, ContentSupplier], ...]

    def _gen_header(self) -> Generator[bytes, None, None]:
        yield b'#!' + self.shell_path

        if self.trace:
           yield b'set +x'
        
        yield f'''decode() {{
     base64 --decode | gunzip - > "${1}"
}}'''.encode('utf-8')

    @staticmethod
    def _gen_per_file(name: str, 
                      is_clear: bool, 
                      contents: ContentSupplier) -> Generator[bytes, None, None]:
        directory_name = path.split(name)[0]
        un_encoded_bytes = contents()

        if directory_name is not None and directory_name != '':
            yield f'mkdir -p {directory_name}'.encode('utf-8')

        if is_clear:
            if _END_MARKER_CONDITION_BYTES in un_encoded_bytes:
                raise ValueError(f"File {name} should not contain the end sequence {_END_MARKER_STR}")
            yield f'cat > {name} <<"{_END_MARKER_STR}"'.encode('utf-8')
            yield un_encoded_bytes
            yield _END_MARKER_BYTES
        else:
            encoded_bytes = b64encode(_compress(un_encoded_bytes))

            yield f'decode {name} <<"{_END_MARKER_STR}"'.encode('utf-8')
            yield encoded_bytes
            yield _END_MARKER_BYTES

    def _gen(self) -> Generator[bytes, None, None]:
        yield from self._gen_header()

        known_files = set()

        pattern = globs_to_pattern(self.clear_globs)
        for (file_name, supplier) in self.elements:
            if file_name in known_files:
                raise ValueError(f"Received the same file twice {file_name}")
            known_files.add(file_name)
            is_clear = pattern is not None and pattern.search(file_name) is not None
            yield from self._gen_per_file(file_name, is_clear, supplier)
        
        # Do not separate those two statements!
        yield self.final_command
        yield b'exit $?'

    def gen_bytes(self) -> bytes:
        return b'\n'.join(self._gen())

@dataclass
class DataSourceWithPrefix(object):
    data_source: DataSource
    prefix: str

    def get_files(self) -> Iterable[Tuple[str, ContentSupplier]]:
        return ((self.prefix + file_name, content_supplier) for 
                (file_name, content_supplier) in self.data_source.provide_files())

@dataclass
class SharikBuilder(object):
    final_command: Union[bytes, str]
    trace: bool = False
    shell_path: bytes = b'/bin/sh'
    components: List[DataSourceWithPrefix] = field(default_factory=list)
    clear_globs: List[str] = field(default_factory=list)

    def add_data_source(self, data_source: DataSource, prefix: str='') -> None:
        self.components.append(DataSourceWithPrefix(data_source, prefix))

    def add_clear_glob(self, clear_glob: str) -> None:
        self.clear_globs.append(clear_glob)

    def normalized(self) -> Tuple[Tuple[str, ContentSupplier], ...]:
        result = []
        
        file_name_to_data_source = {}
        for data_source_with_prefix in self.components:
            for (file_name, content_supplier) in data_source_with_prefix.get_files():
                result.append((file_name, content_supplier))
                previous_source = file_name_to_data_source.get(file_name)
                if previous_source is not None:
                    raise ValueError(f"More than one source for the file name {file_name}. " \
                                     f"Previous source: {previous_source}, current one {data_source_with_prefix}")
                file_name_to_data_source[file_name] = data_source_with_prefix

        result.sort(key=lambda pair: pair[0])
        return tuple(result)

    def build(self) -> bytes:
        if isinstance(self.final_command, bytes):
            command_bytes = self.final_command
        else:
            command_bytes = self.final_command.encode('utf-8')

        return _SharikShellGenerator(
            self.shell_path,
            command_bytes,
            self.trace,
            self.clear_globs, 
            self.normalized()).gen_bytes()
