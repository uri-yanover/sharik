#!/usr/bin/env python
import click
from typing import Tuple
from .data_sources import InlineDataSource, FileDataSource
from .builder import SharikBuilder

def _process_inline(_ctx: click.Context, values: Tuple[str]) -> Tuple[Tuple[str, bytes], ...]:
    def _gen_element(value):
        first_equals = value.find('=')
        if first_equals <= 0:
            raise click.BadParameter(f'Must be of the form key=value')
        return value[:first_equals], value[first_equals+1:].encode('utf-8')
    return tuple(_gen_element(value) for value in values)

@click.command()
@click.option('--command', type=str, required=True, help="Shell command to be run after unpacking")
@click.option('--add', type=click.Path(), multiple=True, help="File to be added")
@click.option('--inline', type=str, multiple=True, help="Inline parameters to be added",
              callback=_process_inline)
@click.option('--clear-glob', type=str, multiple=True, 
              help="Files to be represented without compression/encoding")

def cli_main(command: str, 
             add: Tuple[str, ...],
             inline: Tuple[Tuple[str, bytes], ...],
             clear_glob: Tuple[str, ...]):
    builder = SharikBuilder(command.encode('utf-8'))
    for element in add:
        builder.add_data_source(FileDataSource(element))
    if len(inline) > 0:
        builder.add_data_source(InlineDataSource(inline))
    for element in clear_glob:
        builder.add_clear_glob(element)
    print(builder.build())

if __name__ == '__main__':
    cli_main()
