from unittest import TestCase
from sharik.builder import SharikBuilder
from sharik.data_sources import InlineDataSource, FileDataSource

from sys import stderr
from os.path import dirname, basename, join

_OWN_FILE=basename(__file__)
_OWN_DIR=dirname(__file__)
_PARENT_DIR=join(_OWN_DIR, '..')


class TestSanity(TestCase):
    def testSanity(self):
        f = SharikBuilder(b'ls -la')
        f.add_data_source(InlineDataSource((('foo', b'hello world' * 33),)))
        f.add_data_source(InlineDataSource((('bar', b'hello world'),)))
        f.add_data_source(InlineDataSource((('dir/dfs', b'hakuna matata'),)))

        f.add_clear_glob('dir/*')
        stderr.write(f.build().decode('utf-8'))

    def testPrefix(self):
        f = SharikBuilder(b'ls -la')
        f.add_data_source(InlineDataSource((('foo', b'a' * 33),)))
        f.add_data_source(InlineDataSource((('foo', b'b' * 33),)), prefix='test/')
        f.add_clear_glob('foo')

        result = f.build().decode('utf-8')

        self.assertIn('a' * 33, result)
        self.assertIn('b' * 33, result)
        self.assertIn('test/foo', result)

    def testRecursive(self):
        for recursive_status in (False, True):
            f = SharikBuilder(b'ls -la')
            f.add_data_source(FileDataSource(_PARENT_DIR, recursive_status, ('*.py',), ()))
            result = f.build().decode('utf-8')
            self.assertIn('abstract.py', result)
            self.assertIn('data_sources.py', result)
            self.assertEqual(_OWN_FILE in result, recursive_status)

    def testWhitelist(self):
        f = SharikBuilder(b'ls -la')
        anchor = 'data_sources.py'
        f.add_data_source(FileDataSource(_PARENT_DIR, False, (anchor,), ()))
        result = f.build().decode('utf-8')
        self.assertIn(anchor, result)

    def testBlacklist(self):
        f = SharikBuilder(b'ls -la')
        anchor_out = 'data_sources.py'
        anchor_in = 'builder.py'
        f.add_data_source(FileDataSource(_PARENT_DIR, False, ('*.py',), (anchor_out,)))
        result = f.build().decode('utf-8')
        self.assertNotIn(anchor_out, result)            
        self.assertIn(anchor_in, result)

    def testType(self):
        try:
            SharikBuilder('ls -la')
            self.fail("Should not have accepted a parameter that's not bytes")
        except:
            pass