from __future__ import annotations

import os
import shutil
import tarfile
import zipfile
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Any
from typing import Callable
from typing import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests


class CommaUtils:
    def __init__(self) -> None:
        self.user_home_dir = os.path.expanduser('~')
        self.opt_dir = os.path.join(self.user_home_dir, 'opt')
        self.comma_dir = os.path.join(self.opt_dir, 'comma')
        self.temp_dir = os.path.join(self.comma_dir, 'temp')
        self.cache_dir = os.path.join(self.comma_dir, 'cache')
        self.download_cache_dir = os.path.join(self.cache_dir, 'download')

        # print(list(vars(self).values()))
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.download_cache_dir, exist_ok=True)


comma_utils = CommaUtils()


@contextmanager
def temp_dir_context() -> Generator[str, None, None]:
    with TemporaryDirectory(dir=comma_utils.temp_dir) as temp_dir:
        yield temp_dir


@contextmanager
def unpacker_context(filename: str) -> Generator[str, None, None]:
    from rich.halo import FHalo
    with temp_dir_context() as temp_dir:
        with (
                zipfile.ZipFile(filename)  # type:ignore
                if filename.endswith('.zip')
                else tarfile.open(filename)
        ) as archive:
            with FHalo(f'Extracting {filename}...') as halo:
                archive.extractall(temp_dir)
                halo.succeed()
        yield temp_dir


def quick_deleter(path: str) -> None:
    if os.path.exists(path):
        return
    from rich.halo import FHalo
    with FHalo(f'Deleting {path}...') as halo:
        with temp_dir_context() as temp_dir:
            temp = os.path.join(temp_dir, 'temp')
            shutil.move(path, temp)
        halo.succeed()


@contextmanager
def progress_bar(*, total_size: int, filename: str) -> Generator[Callable[[int], None], None, None]:
    # from tqdm import tqdm
    # with tqdm(total=total_size, unit='iB', unit_scale=True) as progress_bar:
    #     yield lambda chunk_size: progress_bar.update(chunk_size)

    from rich.progress import (
        BarColumn,
        DownloadColumn,
        Progress,
        TextColumn,
        TimeRemainingColumn,
        TransferSpeedColumn,
    )

    progress = Progress(
        TextColumn('[bold blue]{task.fields[filename]}', justify='right'),
        BarColumn(bar_width=None),
        '[progress.percentage]{task.percentage:>3.1f}%',
        '•',
        DownloadColumn(),
        '•',
        TransferSpeedColumn(),
        '•',
        TimeRemainingColumn(),
        transient=True,
    )
    with progress as progress_bar:
        task_id = progress_bar.add_task(
            'Downloading', filename=filename, total=total_size,
        )
        yield lambda chunk_size: progress_bar.update(task_id=task_id, advance=chunk_size)


@contextmanager
def download_context(
    *,
    url: str,
    session: requests.Session | None = None,
    filename: str | None = None,
    **kwargs: Any,
) -> Generator[str, None, None]:
    import requests

    filename = filename or url.split('/')[-1]
    session = session or requests.Session()

    with temp_dir_context() as temp_dir:
        with session.get(url, stream=True, **kwargs) as response:
            response.raise_for_status()
            # with suppress(KeyError):
            #     filename, *_ = re.findall('filename=(.+)', response.headers['Content-Disposition']) + [filename]
            total_size = int(response.headers.get('content-length', 0))
            with progress_bar(total_size=total_size, filename=filename) as progress_callback:
                full_path = os.path.join(temp_dir, filename)
                with open(full_path, 'wb') as file:
                    try:
                        for chunk in response.iter_content(chunk_size=4 * 1024):
                            progress_callback(len(chunk))
                            file.write(chunk)
                    except KeyboardInterrupt:
                        raise SystemExit(1)
        yield full_path
