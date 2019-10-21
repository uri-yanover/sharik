from unittest import TestCase

from sharik.builder import SharikBuilder
from sharik.data_sources import InlineDataSource, FileDataSource

class TestSanity(TestCase):
    def testSanity(self):
        f = SharikBuilder(b'ls -la')
        f.add_data_source(InlineDataSource((('foo', b'hello world' * 33),)))
        f.add_data_source(InlineDataSource((('bar', b'hello world'),)))
        f.add_data_source(InlineDataSource((('dir/dfs', b'hakuna matata'),)))

        f.add_clear_glob('dir/*')

        from sys import stderr
        stderr.write(f.build().encode('utf-8'))

        print(f.build())