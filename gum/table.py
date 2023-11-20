# Usage: gum table
# Render a table of data
# Flags:
#   -h, --help                   Show context-sensitive help.
#   -v, --version                Print the version number
#   -s, --separator=","          Row separator
#   -c, --columns=COLUMNS,...    Column names
#   -w, --widths=WIDTHS,...      Column widths
#       --height=10              Table height
#   -f, --file=""                file path
from __future__ import annotations

import csv
import subprocess
import tempfile
from typing import Sequence
from typing import TypeAlias

_CSV_CELL: TypeAlias = str | int | float | bool
_CSV_DATA: TypeAlias = Sequence[dict[str, _CSV_CELL]] | str


def gum_table(
    data_or_file: _CSV_DATA,
    separator: str | None = None,
    columns: list[str] = [],
    widths: list[int] = [],
    height: int | None = None,
) -> str | None:
    if not data_or_file:
        return None
    cmd = ['gum', 'table']
    if separator:
        cmd.append(f'--separator={separator}')
    if columns:
        cmd.append(f"--columns={','.join(columns)}")
    if widths:
        cmd.append(f"--widths={','.join(map(str, widths))}")
    if height:
        cmd.append(f'--height={height}')
    with tempfile.NamedTemporaryFile(mode='w') as f:
        filename = data_or_file if isinstance(data_or_file, str) else f.name
        if not isinstance(data_or_file, str):
            dict_writer = csv.DictWriter(f, fieldnames=data_or_file[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(data_or_file)
        cmd.append(f'--file={filename}')
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, encoding='utf-8').stdout.strip()
        return result if result else None


if __name__ == '__main__':
    r = gum_table(data_or_file='/Users/flavio/Downloads/international-trade-june-2023-quarter/revised.csv')
    print(f'{r=}')
