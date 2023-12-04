#!/usr/bin/env bash
"""":
exec "${LATEST_PYTHON:-$(which python3.12 || which python3.11 || which python3.10 || which python3.9 || which python3.8 || which python3.7 || which python3 || which python)}" "${0}" "${@}"
"""
from __future__ import annotations

import argparse
import configparser
import dataclasses
import glob
import itertools
import json
import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from abc import ABC
from abc import abstractmethod
from collections import ChainMap
from collections import Counter
from configparser import SectionProxy
from contextlib import contextmanager
from contextlib import suppress
from dataclasses import asdict
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import path as importlib_path
from typing import Any
from typing import Generator
from typing import List
from typing import Literal
from typing import Mapping
from typing import NamedTuple
from typing import overload
from typing import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Protocol  # python3.8+
    from typing import Self
else:
    Protocol = object


def input_tty(prompt: str | None = None) -> str:
    with open('/dev/tty') as tty:
        if prompt:
            print(prompt, end='', file=sys.stderr)
        return tty.readline().strip()


def selection(options: list[str]) -> str | None:
    if len(options) == 1:
        return options[0]
    print('Please select one of the following options:', file=sys.stderr)
    try:
        return options[int(input_tty('\n'.join(f'{i}: {x}' for i, x in enumerate(options)) + '\nEnter Choice: ') or 0)]
    except IndexError:
        return None


@lru_cache(maxsize=1)
def list_executables_in_path() -> List[str]:
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    executables = []
    for path_dir in path_dirs:
        if os.path.isdir(path_dir):
            for file_name in os.listdir(path_dir):
                file_path = os.path.join(path_dir, file_name)
                if os.access(file_path, os.X_OK) and not os.path.isdir(file_path):
                    executables.append(file_path)
    return executables


@lru_cache(maxsize=1)
def latest_python() -> str:
    executables = list_executables_in_path()
    pythons = [
        x for x in executables
        if os.path.basename(x).startswith('python') and not x.endswith('config')
    ]
    return max(pythons, key=lambda x: tuple(int(y) for y in os.path.basename(x).split('python')[1].split('.') if y.isdigit()))


def newest_python() -> str:
    return os.path.realpath(
        subprocess.run(
            ('{ which python3.12 || which python3.11 || which python3.10 || which python3.9 || which python3.8 || which python3.7 || which python3 || which python; } 2>/dev/null'),
            shell=True,
            capture_output=True,
            encoding='utf-8',
        )
        .stdout
        .strip(),
    )


class ExecutableProvider(Protocol):
    def get_executable(self) -> str:
        ...

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        ...

    def _mdict(self) -> dict[str, Any]:
        ...


class _ToolInstallerBase(ABC):
    BIN_INSTALL_DIR: str = os.environ.get(
        'TOOL_INSTALLER_BIN_DIR', os.path.join(
            os.path.expanduser('~'), '.local', 'bin',
        ),
    )

    @staticmethod
    def make_executable(filename: str) -> str:
        os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)
        return filename

    @abstractmethod
    def get_executable(self) -> str:
        ...

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            (self.get_executable(), *args),
            text=True,
            errors='ignore',
            encoding='utf-8',
            capture_output=True,
        )

    def _mdict(self) -> dict[str, Any]:
        m_asdict: dict[str, str] = (
            self._asdict()  # type:ignore
            if hasattr(self, '_asdict')
            else asdict(self)  # type:ignore
        )

        with suppress(Exception):
            anno: dict[str, dataclasses.Field] = self.__class__.__dataclass_fields__  # type:ignore
            for k, v in anno.items():
                if m_asdict[k] == v.default:
                    del m_asdict[k]

        return {
            'class': self.__class__.__name__,
            **{
                key: value
                for key, value in m_asdict.items()
                if value is not None and not key.isupper()
            },
        }


@dataclass
class GitProjectInstallSource(_ToolInstallerBase):
    git_url: str
    path: str
    tag: str = 'master'
    pull: bool = False
    GIT_PROJECT_DIR: str = os.environ.get(
        'TOOL_INSTALLER_GIT_PROJECT_DIR', os.path.join(
            os.path.expanduser('~'), 'opt', 'git_projects',
        ),
    )

    def get_executable(self) -> str:
        git_project_location = os.path.join(
            self.GIT_PROJECT_DIR, '_'.join(self.git_url.split('/')[-1:]),
        )
        git_bin = os.path.join(git_project_location, self.path)
        if not os.path.exists(git_bin):
            subprocess.run(
                (
                    'git', 'clone', '-b', self.tag,
                    self.git_url, git_project_location,
                ), check=True,
            )
        elif self.pull:
            subprocess.run(('git', '-C', git_project_location, 'pull'))
        return self.make_executable(git_bin)


@dataclass
class ShivInstallSource(_ToolInstallerBase):
    package: str
    command: str | None = None

    def get_executable(self) -> str:
        command = self.command or self.package
        bin_path = os.path.join(self.BIN_INSTALL_DIR, command)
        if not os.path.exists(bin_path):
            shiv_executable = UrlInstallSource(
                url='https://github.com/linkedin/shiv/releases/download/1.0.3/shiv', rename='shiv',
            ).get_executable()
            subprocess.run(
                (
                    newest_python(),
                    shiv_executable,
                    '-c', command,
                    '-o', bin_path,
                    self.package,
                ),
                check=True,
            )
        return self.make_executable(bin_path)


@dataclass
class PipxInstallSource(_ToolInstallerBase):
    package: str
    command: str | None = None

    def get_executable(self) -> str:
        command = self.command or self.package
        bin_path = os.path.join(self.BIN_INSTALL_DIR, command)
        if not os.path.exists(bin_path):
            pipx_cmd = GithubReleaseLinks(project='pypa', user='pipx', rename='pipx').get_executable()
            env = {
                **os.environ,
                'PIPX_DEFAULT_PYTHON': newest_python(),
                'PIPX_BIN_DIR': self.BIN_INSTALL_DIR,
                # 'PIPX_HOME': self.bin_dir,
            }
            subprocess.run(
                (
                    pipx_cmd, 'install', '--force',
                    self.package,
                ), check=True, env=env,
            )
        return bin_path


class InternetInstaller(_ToolInstallerBase, ABC):
    PACKAGE_INSTALL_DIR: str = os.environ.get(
        'TOOL_INSTALLER_PACKAGE_DIR', os.path.join(os.path.expanduser('~'), 'opt', 'packages'),
    )

    @staticmethod
    def uncompress(filename: str) -> zipfile.ZipFile | tarfile.TarFile:
        return zipfile.ZipFile(filename) if filename.endswith('.zip') else tarfile.open(filename)

    @staticmethod
    def find_executable(directory: str, executable_name: str) -> str | None:
        glob1 = glob.iglob(
            os.path.join(
                directory, '**', executable_name,
            ), recursive=True,
        )
        glob2 = glob.iglob(
            os.path.join(
                directory, '**', f'{executable_name}*',
            ), recursive=True,
        )
        return next((x for x in itertools.chain(glob1, glob2) if (os.path.isfile(x)) and not os.path.islink(x)), None)

    @staticmethod
    def get_request(url: str) -> str:
        import urllib.request
        headers = {}
        if 'github' in url and 'GITHUB_TOKEN' in os.environ:
            headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as f:
            return f.read().decode('utf-8')

    @staticmethod
    @contextmanager
    def download_context(url: str) -> Generator[str, None, None]:
        import urllib.request
        logging.info(f'Downloading: {url}')
        derive_name = os.path.basename(url)
        with tempfile.TemporaryDirectory() as tempdir:
            download_path = os.path.join(tempdir, derive_name)
            headers = {}
            if 'github' in url and 'GITHUB_TOKEN' in os.environ:
                headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
            req = urllib.request.Request(url, headers=headers)
            with open(download_path, 'wb') as file:
                with urllib.request.urlopen(req) as f:
                    file.write(f.read())
            yield download_path

    @classmethod
    def executable_from_url(cls, url: str, rename: str | None = None) -> str:
        """
        url must point to executable file.
        """
        rename = rename or os.path.basename(url)
        executable_path = os.path.join(cls.BIN_INSTALL_DIR, rename)
        if not os.path.exists(executable_path):
            os.makedirs(cls.BIN_INSTALL_DIR, exist_ok=True)
            with cls.download_context(url) as download_file:
                shutil.move(download_file, executable_path)
        return cls.make_executable(executable_path)

    @classmethod
    def executable_from_package(
        cls,
        package_url: str,
        executable_name: str,
        package_name: str | None = None,
        rename: str | None = None,
    ) -> str:
        """
        Get the executable from a online package.
        package_url         points to zip/tar file.
        executable_name     file to looked for in package.
        package_name        what should the package be rename to.
        rename              The name of the file place in bin directory
        """
        package_name = package_name or os.path.basename(package_url)
        package_path = os.path.join(cls.PACKAGE_INSTALL_DIR, package_name)
        if not os.path.exists(package_path) or cls.find_executable(package_path, executable_name) is None:
            with cls.download_context(package_url) as tar_zip_file:
                with tempfile.TemporaryDirectory() as tempdir:
                    temp_extract_path = os.path.join(tempdir, 'temp_package')
                    with cls.uncompress(tar_zip_file) as untar_unzip_file:
                        untar_unzip_file.extractall(temp_extract_path)
                    os.makedirs(cls.PACKAGE_INSTALL_DIR, exist_ok=True)
                    shutil.move(temp_extract_path, package_path)

        result = cls.find_executable(package_path, executable_name)
        if not result:
            logging.error(f'{executable_name} not found in {package_path}')
            raise SystemExit(1)

        executable = cls.make_executable(result)
        rename = rename or executable_name
        os.makedirs(cls.BIN_INSTALL_DIR, exist_ok=True)
        symlink_path = os.path.join(cls.BIN_INSTALL_DIR, rename)
        if os.path.isfile(symlink_path):
            if not os.path.islink(symlink_path):
                logging.info(
                    f'File is already in {cls.BIN_INSTALL_DIR} with name {os.path.basename(executable)}',
                )
                return executable
            elif os.path.realpath(symlink_path) == os.path.realpath(executable):
                return symlink_path
            else:
                os.remove(symlink_path)

        os.symlink(executable, symlink_path, target_is_directory=False)
        return symlink_path


@dataclass
class GithubScriptInstallSource(InternetInstaller):
    user: str
    project: str
    path: str | None = None
    tag: str = 'master'
    rename: str | None = None

    def get_executable(self) -> str:
        """
        Download file from github repo.

        user        github username.
        project     github project name.
        path        relative path of the file in github repo.
        tag         branch/tag name.
        rename      what should the file be rename as.
        """
        path = self.path or self.project
        url = f'https://raw.githubusercontent.com/{self.user}/{self.project}/{self.tag}/{path}'
        return self.executable_from_url(url=url, rename=self.rename)


@dataclass
class UrlInstallSource(InternetInstaller):
    url: str
    rename: str | None = None

    def get_executable(self) -> str:
        return self.executable_from_url(url=self.url, rename=self.rename)


@dataclass
class ZipTarInstallSource(InternetInstaller):
    package_url: str
    executable_name: str
    package_name: str | None = None
    rename: str | None = None

    def get_executable(self) -> str:
        return self.executable_from_package(
            package_url=self.package_url,
            executable_name=self.executable_name,
            package_name=self.package_name,
            rename=self.rename,
        )


class LinkInstaller(InternetInstaller, ABC):
    @property
    @abstractmethod
    def binary(self) -> str:
        ...

    @property
    @abstractmethod
    def rename(self) -> str | None:
        ...

    @property
    @abstractmethod
    def package_name(self) -> str | None:
        ...

    @abstractmethod
    def links(self) -> List[str]:
        ...

    def get_executable(self) -> str:
        executable_path = os.path.join(
            self.BIN_INSTALL_DIR, self.rename or self.binary,
        )
        if os.path.exists(executable_path):
            return executable_path

        return self.install_best(
            links=self.links(),
            binary=self.binary,
            rename=self.rename,
            package_name=self.package_name,
        )

    def install_best(self, links: Sequence[str], binary: str, rename: str | None = None, package_name: str | None = None) -> str:
        rename = rename or binary
        download_url = BestLinkService().pick(links)
        if not download_url:
            logging.error(
                f'Could not choose appropiate download from {rename}',
            )
            raise SystemExit(1)
        basename = os.path.basename(download_url)
        if basename.endswith('.zip') or '.tar' in basename or basename.endswith('.tgz') or basename.endswith('.tbz'):
            return self.executable_from_package(
                package_url=download_url,
                executable_name=binary,
                package_name=package_name,
                rename=rename,
            )
        return self.executable_from_url(download_url, rename=rename)


class BestLinkService(NamedTuple):
    uname: platform.uname_result = platform.uname()

    def pick(self, links: Sequence[str]) -> str | None:
        links = self.filter(links)
        return selection(links) or sorted(links, key=len)[-1]

    def filter(self, links: Sequence[str]) -> list[str]:
        """
        Will look at the urls and based on the information it has will try to pick the best one.

        links   links to consider.
        """
        if not links:
            return []
        if len(links) == 1:
            return [links[0]]

        links = self.filter_out_invalid(links)
        links = self.filter_system(links, self.uname.system)
        links = [x for x in links if not x.endswith('.rpm')] or links
        links = [x for x in links if not x.endswith('.deb')] or links
        links = self.filter_machine(links, self.uname.machine)
        links = [x for x in links if 'musl' in x.lower()] or links
        links = [x for x in links if 'armv7' not in x.lower()] or links

        return sorted(links, key=len)

    def filter_system(self, links: list[str], system: str) -> list[str]:
        """
        links
        system  darwin,linux,windows
        """
        system_patterns = {
            'darwin': 'darwin|apple|macos|osx',
            'linux': 'linux|\\.deb',
            'windows': 'windows|\\.exe',
        }

        system = system.lower()
        if system not in system_patterns or not links or len(links) == 1:
            return links

        pat = re.compile(system_patterns[system])
        filtered_links = [
            x for x in links if pat.search(
                os.path.basename(x).lower(),
            )
        ]
        return filtered_links or links

    def filter_machine(self, links: list[str], machine: str) -> list[str]:
        machine_patterns = {
            'x86_64': 'x86_64|amd64|x86',
            'arm64': 'arm64|arch64',
            'aarch64': 'aarch64|armv7l|armv7|arm64',
        }

        if not links or len(links) == 1:
            return links

        machine = machine.lower()
        pat = re.compile(machine_patterns.get(machine, machine))
        filtered_links = [
            x for x in links if pat.search(
                os.path.basename(x).lower(),
            )
        ]

        return filtered_links or links

    def filter_out_invalid(self, links: Sequence[str]) -> list[str]:
        return [
            x
            for x in links
            if not re.search(
                '\\.txt|license|\\.md|\\.sha256|\\.sha256sum|checksums|\\.asc|\\.sig|src|\\.sbom',
                os.path.basename(x).lower(),
            )
        ]


@dataclass
class ZigLinks(LinkInstaller):
    binary: str = 'zig'
    rename: str | None = None
    package_name: str = 'zig'

    def links_scraper(self, obj: Any) -> Generator[str, None, None]:
        if not isinstance(obj, dict):
            return
        for k, v in obj.items():
            if isinstance(v, dict):
                yield from self.links_scraper(v)
            elif isinstance(v, list):
                yield from (self.links_scraper(e) for e in v)  # type: ignore
            elif k == 'tarball':
                yield v

    def links(self) -> List[str]:
        url = 'https://ziglang.org/download/index.json'
        return list(self.links_scraper(json.loads(self.get_request(url))['master']))


# @dataclass
# class RCloneLinks(LinkInstaller):
#     binary: str = 'rclone'
#     rename: str | None = None
#     package_name: str = 'rclone'

#     def links(self) -> List[str]:
#         url = 'https://downloads.rclone.org/'
#         return [
#             url + line.split('"', maxsplit=2)[1][2:]
#             for line in self.get_request(url).splitlines()
#             if '<a href="./rclone-current-' in line
#         ]


# @dataclass
# class GraalVMLinks(LinkInstaller):
#     binary: str = 'native-image'
#     rename: str | None = None
#     package_name: str = 'native-image'

#     def links(self) -> List[str]:
#         url = 'https://www.oracle.com/java/technologies/downloads/'
#         return [
#             line.split('"', maxsplit=2)[1]
#             for line in self.get_request(url).splitlines()
#             if '<a href="https://download.oracle.com/graalvm' in line
#         ]


@dataclass
class NodeLinks(LinkInstaller):
    binary: Literal['node', 'npm', 'npx'] = 'node'
    rename: str | None = None
    package_name: str | None = 'nodejs'

    def links(self) -> List[str]:
        url = 'https://nodejs.org/dist/latest/'
        return [
            url + line.split('"', maxsplit=2)[1]
            for line in self.get_request(url).splitlines()
            if '<a href="node-v' in line
        ]


@dataclass
class HerokuLinks(LinkInstaller):
    binary: str = 'heroku'
    rename: str | None = None
    package_name: str = 'heroku'

    def links(self) -> List[str]:
        url = 'https://devcenter.heroku.com/articles/heroku-cli'
        return [
            line.split('"', maxsplit=2)[1]
            for line in self.get_request(url).splitlines()
            if '<a href="https://cli-assets.heroku.com/channels/stable/heroku-' in line and 'manifest' not in line
        ]


@dataclass
class GithubReleaseLinks(LinkInstaller):
    user: str
    project: str
    tag: str = 'latest'
    _binary: str | None = None
    rename: str | None = None
    base_url: str = 'https://github.com'

    @property
    def binary(self) -> str:
        return self._binary or self.project

    @property
    def package_name(self) -> str:
        return f'{self.user}_{self.project}'

    def links(self) -> list[str]:
        url = f'{self.base_url}/{self.user}/{self.project}/releases/{"latest" if self.tag == "latest" else f"tag/{self.tag}"}'
        html = self.get_request(url)
        # download_links = [
        #     self.base_url + link
        #     for link in re.findall(f'/{self.user}/{self.project}/releases/download/[^"]+', html)
        # ]
        download_links: list[str] = []
        if not download_links:
            # logging.error('Github is now using lazy loading fragments :(')
            assets_urls = [
                self.base_url + link
                for link in re.findall(f'/{self.user}/{self.project}/releases/expanded_assets/[^"]+', html)
            ]
            if assets_urls:
                html = self.get_request(assets_urls[0])
                download_links = [
                    self.base_url + link
                    for link in re.findall(f'/{self.user}/{self.project}/releases/download/[^"]+', html)
                ]
            else:
                logging.error('Not assets urls')

        return download_links


# @dataclass
# class ScriptInstaller(InternetInstaller):
#     """
#     Download setup script
#     Source script
#     Add Environment variables
#     Command could be executable or bash function

#     """
#     scritp_url: str
#     command: str

#     def get_executable(self) -> str:
#         with self.download_context(self.scritp_url) as path:
#             self.make_executable(path)
#             subprocess.run([path, '--help'])

#         # return super().get_executable()


@dataclass
class GroupUrlInstallSource(LinkInstaller):
    _links: List[str]
    binary: str
    rename: str | None = None
    package_name: str | None = None

    def links(self) -> List[str]:
        return self._links


# 'rustup': ScriptInstaller(scritp_url='https://sh.rustup.rs', command='rustup'),
# 'sdk': ScriptInstaller(scritp_url='https://get.sdkman.io', source_script='$HOME/.sdkman/bin/sdkman-init.sh', command='sdk'),


class RunToolConfig:
    _tools: Mapping[str, ExecutableProvider]

    def __init__(self) -> None:
        self._tools = ChainMap(
            self.__load_config__(),
            self.parse_json_obj(parse_ini(get_builtin_config())),
        )

    @classmethod
    def __config_file_path__(cls) -> str:
        return os.path.expanduser(os.getenv('RUNTOOL_CONFIG', '~/.config/runtool/runtool.ini'))

    @classmethod
    def __load_config__(cls) -> dict[str, ExecutableProvider]:
        filename = cls.__config_file_path__()
        if not os.path.exists(filename):
            return {}

        return cls.parse_json_obj(parse_ini(filename))

    @classmethod
    def parse_json_obj(cls, raw_obj: Mapping[str, Mapping[str, str]]) -> dict[str, ExecutableProvider]:
        return {k: cls.__from_obj__(dict(v)) for k, v in raw_obj.items()}

    @staticmethod
    def __from_obj__(obj: dict[str, str]) -> ExecutableProvider:
        class_name = obj.pop('class')
        obj.pop('description', None)  # TODO: add description to dataclass
        return getattr(sys.modules[__name__], class_name)(**obj)

    def save(self) -> None:
        final_obj = {
            k: v._mdict()
            for k, v in sorted(self._tools.items())
        }

        with open('/tmp/RUNCONFIG.json', 'w') as f:
            json.dump(final_obj, f, indent=4)

    def run(self, command: str, *args: str) -> subprocess.CompletedProcess[str]:
        return self._tools[command].run(*args)

    @classmethod
    @lru_cache(maxsize=1)
    def get_instance(cls) -> RunToolConfig:
        return cls()

    @classmethod
    def tool_names(cls) -> list[str]:
        return sorted(cls.get_instance()._tools.keys())

    @classmethod
    def get_tool(cls, command: str) -> ExecutableProvider:
        return cls.get_instance()._tools[command]

    @classmethod
    def get_executable(cls, command: str) -> str:
        return cls.get_tool(command).get_executable()


def get_builtin_config() -> str:
    with importlib_path(__package__, 'runtool.ini') as path:
        return path.as_posix()


def parse_ini(filename: str) -> dict[str, SectionProxy]:
    config = configparser.ConfigParser()
    config.read(filename)
    return {k: config[k] for k in config.sections()}


class CLIApp(Protocol):
    COMMAND_NAME: str
    DESCRIPTION: str

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION)
        return parser

    @overload
    @classmethod
    def parse_args(cls, argv: Sequence[str] | None) -> Self:
        ...

    @overload
    @classmethod
    def parse_args(cls, argv: Sequence[str] | None, *, allow_unknown_args: Literal[False]) -> Self:
        ...

    @overload
    @classmethod
    def parse_args(cls, argv: Sequence[str] | None, *, allow_unknown_args: Literal[True]) -> tuple[Self, list[str]]:
        ...

    @classmethod
    def parse_args(cls, argv: Sequence[str] | None = None, *, allow_unknown_args: bool = False) -> tuple[Self, list[str]] | Self:
        return cls.parser().parse_known_args(argv) if allow_unknown_args else cls.parser().parse_args(argv)  # type:ignore

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        ...


class CLIWhich(CLIApp):
    COMMAND_NAME = 'which'
    DESCRIPTION = 'Show executable file path.'
    tool: str

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION, add_help=False)
        parser.add_argument('tool', choices=sorted(RunToolConfig.tool_names()))
        return parser

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        args = cls.parse_args(argv)
        print(RunToolConfig.get_executable(args.tool))
        return 0


class CLIRun(CLIApp):
    COMMAND_NAME = 'run'
    DESCRIPTION = 'Run tool.'
    tool: str

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION, add_help=False)
        parser.add_argument('tool', choices=sorted(RunToolConfig.tool_names()))
        return parser

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        args, rest = cls.parse_args(argv, allow_unknown_args=True)
        tool = RunToolConfig.get_executable(args.tool)
        cmd = (tool, *rest)
        os.execvp(cmd[0], cmd)


class CLIFilterLinks(CLIApp):
    COMMAND_NAME = 'filter-links'
    DESCRIPTION = 'Filter links by system.'
    selector: str

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION)
        parser.add_argument('--selector', choices=('filter', 'pick'), default='pick')
        return parser

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        stdin_lines = []
        if not sys.stdin.isatty():
            stdin_lines = [x.strip() for x in sys.stdin]

        args, rest = cls.parse_args(argv, allow_unknown_args=True)
        options = [*stdin_lines, *rest]
        if not options:
            return 1
        if len(options) == 1:
            print(options[0])
            return 0
        service = BestLinkService()
        if args.selector == 'pick':
            result = service.pick(options)
            if not result:
                return 1
            print(result)
        elif args.selector == 'filter':
            results = service.filter(options)
            if not results:
                return 1
            for line in results:
                print(line)
        return 0


class GhInstall(CLIApp):
    COMMAND_NAME = 'gh-install'
    DESCRIPTION = 'Install from github release.'
    user: str
    project: str
    binary: str | None
    rename: str | None
    github: str

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION)
        parser.add_argument('user')
        parser.add_argument('project')
        parser.add_argument('--binary', default=None)
        parser.add_argument('--rename', default=None)
        parser.add_argument('--github', default='https://github.com')
        return parser

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        args = cls.parse_args(argv)
        gh = GithubReleaseLinks(
            user=args.user,
            project=args.project,
            _binary=args.binary,
            rename=args.rename,
            base_url=args.github,
        )

        print(gh.get_executable())
        return 0


class GhLinks(CLIApp):
    COMMAND_NAME = 'gh-links'
    DESCRIPTION = 'Show github release links.'
    user: str
    project: str
    github: str

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION)
        parser.add_argument('user')
        parser.add_argument('project')
        parser.add_argument('--github', default='https://github.com')
        return parser

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        args = cls.parse_args(argv)
        gh = GithubReleaseLinks(
            user=args.user,
            project=args.project,
            base_url=args.github,
        )
        for link in gh.links():
            print(link)

        return 0


class CLILinkInstaller(CLIApp):
    COMMAND_NAME = 'link-installer'
    DESCRIPTION = 'Install from links.'
    links: list[str]
    binary: str | None
    rename: str | None
    package_name: str | None

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION)
        parser.add_argument('links', nargs='+')
        parser.add_argument('--binary', default=None, help='Name of the binary in the package.')
        parser.add_argument('--rename', default=None, help='Rename the binary.')
        parser.add_argument('--package-name', default=None, help='Rename the package.')
        return parser

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        args = cls.parse_args(argv)

        binary = args.binary
        if not binary:
            counter: Counter[str] = Counter()
            for link in args.links:
                for token in os.path.basename(link).split('-'):
                    counter[token] += 1
            binary = counter.most_common(1)[0][0]

        path = LinkInstaller.install_best(
            InternetInstaller,  # type:ignore
            links=args.links,
            binary=binary,
            rename=args.rename,
            package_name=args.package_name,
        )

        print(path)

        return 0


if 'fzf' in (os.path.basename(x) for x in list_executables_in_path()):
    class CLIMultiInstaller(CLIApp):
        COMMAND_NAME = 'multi-installer'
        DESCRIPTION = 'Multi installer.'

        @classmethod
        def run(cls, argv: Sequence[str] | None = None) -> int:
            dct = parse_ini(get_builtin_config())
            result = subprocess.run(('fzf', '--multi'), input='\n'.join(f'{k}: {v.get("description")}' for k, v in dct.items()), text=True, stdout=subprocess.PIPE)
            for line in result.stdout.splitlines():
                print(RunToolConfig.get_executable(line.split(':')[0]))
            return 0


class CLIFormatIni(CLIApp):
    COMMAND_NAME = 'format-ini'
    DESCRIPTION = 'Format ini file.'
    file: list[str]
    output: str

    @classmethod
    def parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=cls.DESCRIPTION)
        parser.add_argument('file', nargs='+')
        parser.add_argument('--output', default='/dev/stdout')
        return parser

    @classmethod
    def run(cls, argv: Sequence[str] | None = None) -> int:
        args = cls.parse_args(argv)

        config = configparser.ConfigParser()
        config.read(args.file)

        order_config = configparser.ConfigParser()
        dct = {
            k: config[k]
            for k in sorted(config.sections(), key=lambda x: (config[x].get('class'), config[x].get('user'), config[x].get('project'), config[x].get('package')))
        }
        for _, v in dct.items():
            if v.get('description', '').strip():
                continue
            clz = v['class']
            github = ''
            if clz == 'PipxInstallSource':
                package = v['package'].split('[')[0]
                if 'github' in package:
                    clz = 'GithubReleaseLinks'
                    github = package
                else:
                    try:
                        pypi_info = json.loads(InternetInstaller.get_request(f'https://www.pypi.org/pypi/{package}/json'))
                        description = pypi_info['info']['summary']
                        if description:
                            v['description'] = description
                            continue
                        else:
                            github = github or next((x for x in pypi_info['info']['project_urls'].values() if 'github' in x), '')
                    except Exception:
                        print(f'Could not get description for {package}', file=sys.stderr)
            if not github and clz in ('GithubScriptInstallSource', 'GithubReleaseLinks'):
                github = v.get('base_url', 'https://github.com') + '/' + v['user'] + '/' + v['project']
            github = github or next((x for x in v.values() if 'github' in x), '')
            if github:
                user, project, *_ = github.split('.com/')[1].split('.git')[0].split('/')
                payload = json.loads(InternetInstaller.get_request(f'https://api.github.com/repos/{user}/{project}'))
                d = payload.get('description')
                if d:
                    v['description'] = d
                    continue
            else:
                print(f'Could not get description for {v["class"]}', file=sys.stderr)

        order_config.read_dict(dct)
        with open(args.output, 'w') as f:
            order_config.write(f)

        return 0


def comma_fixer(argv: Sequence[str] | None = None) -> int:
    """
    Fix comma in json file.
    """
    path_dir = os.path.dirname(sys.argv[0])
    for file_name in os.listdir(path_dir):
        file_path = os.path.join(path_dir, file_name)
        if file_name.startswith('-') and os.access(file_path, os.X_OK) and not os.path.isdir(file_path):
            shutil.move(file_path, os.path.join(path_dir, ',' + file_name[1:]))
    print('Fixed!', file=sys.stderr)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    cli_app = CLIApp.__subclasses__()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('command', choices=[x.COMMAND_NAME for x in cli_app])
    args, rest = parser.parse_known_args(argv)
    command: str = args.command
    for x in cli_app:
        if x.COMMAND_NAME == command:
            raise SystemExit(x.run(rest))
    return 0


# CLIFormatIni.run(['/Users/flavio/projects/,/runtool/runtool.ini'])
if __name__ == '__main__':
    raise SystemExit(main())
