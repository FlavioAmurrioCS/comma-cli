from __future__ import annotations

import contextlib
import datetime
import functools
import json
import logging
import os
import pickle
import sqlite3
import time
from collections import defaultdict
from functools import cached_property
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import TypeVar

from typing_extensions import ParamSpec
from typing_extensions import TypedDict

T = TypeVar('T')
R = TypeVar('R')

CACHE_HOME = os.path.expanduser('~/opt/cache')


class SqliteCache:
    @cached_property
    def connection(self) -> sqlite3.Connection:
        os.makedirs(CACHE_HOME, exist_ok=True)
        return sqlite3.connect(os.path.join(CACHE_HOME, 'comma_sqlite.db'))

    @cached_property
    def cursor(self) -> sqlite3.Cursor:
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY,
                function TEXT,
                args BLOB,
                kwargs BLOB,
                result BLOB,
                timestamp TIMESTAMP DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
            )
        ''')
        connection.commit()
        return cursor

    def get_cached_result(
        self, *,
        func: Callable[..., R],
        args: list[Any],
        kwargs: dict[str, Any],
        time_delta: datetime.timedelta,
    ) -> R:
        # Serialize the arguments and keyword arguments
        pickled_args = pickle.dumps(args)
        pickled_kwargs = pickle.dumps(kwargs)

        # region: Get cached entry
        self.cursor.execute(
            '''
            SELECT result, timestamp FROM cache
            WHERE function = ? AND args = ? AND kwargs = ?
        ''', (func.__name__, pickled_args, pickled_kwargs),
        )
        cached_result = self.cursor.fetchone()
        # endregion: Get cached entry

        if cached_result:
            pickled_result, timestamp = cached_result
            cached_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

            if datetime.datetime.now() < cached_time + time_delta:
                return pickle.loads(pickled_result)
            else:
                # region: Delete expired cache entry
                self.cursor.execute(
                    '''
                    DELETE FROM cache
                    WHERE function = ? AND args = ? AND kwargs = ?
                ''', (func.__name__, pickled_args, pickled_kwargs),
                )
                self.connection.commit()
                # endregion: Delete expired cache entry

        result = func(*args, **kwargs)

        # region: Save result to cache
        pickled_result = pickle.dumps(result)
        self.cursor.execute(
            '''
            INSERT INTO cache (function, args, kwargs, result)
            VALUES (?, ?, ?, ?)
        ''', (func.__name__, pickled_args, pickled_kwargs, pickled_result),
        )
        self.connection.commit()
        # endregion: Save result to cache

        return result

    def __init__(self) -> None:
        self.runtime_cache: dict[str, Any] = {}

    def get_cached_result_quick(
        self, *,
        func: Callable[..., R],
        args: list[Any],
        kwargs: dict[str, Any],
        time_delta: datetime.timedelta,
    ) -> R:
        runtime_cache_key = f'{func.__name__}({args}, {kwargs})'
        if runtime_cache_key not in self.runtime_cache:
            self.runtime_cache[runtime_cache_key] = self.get_cached_result(
                func=func,
                args=args,
                kwargs=kwargs,
                time_delta=time_delta,
            )
        return self.runtime_cache[runtime_cache_key]


sqliteCache = SqliteCache()
P = ParamSpec('P')


def sqlite_cache(
    *,
    days: float = 0,
    seconds: float = 0,
    microseconds: float = 0,
    milliseconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    weeks: float = 0,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    time_delta = datetime.timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )

    def inner(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def __inner__(*args: P.args, **kwargs: P.kwargs) -> R:
            return sqliteCache.get_cached_result_quick(
                func=func,
                args=args,  # type: ignore
                kwargs=kwargs,
                time_delta=time_delta,
            )
        return __inner__
    return inner
###############################################


class CacheEntry(TypedDict):
    args_key: str
    timestampt: datetime.datetime
    result: Any


__CACHE_FILE__ = '/tmp/cache.pickle'


class _DiskCache:
    master_cache: Dict[str, Dict[str, CacheEntry]]

    def __init__(self) -> None:
        self.master_cache = defaultdict(dict)
        with contextlib.suppress(Exception):
            with open(__CACHE_FILE__, 'rb') as f:
                logging.debug('Loading cache file: %s', __CACHE_FILE__)
                self.master_cache.update(pickle.load(f))

    def save(self) -> None:
        with open(__CACHE_FILE__, 'wb') as f:
            pickle.dump(self.master_cache, f)

    def get_cached_result(
        self,
        funcname: str,
        args_key: str,
        time_delta: datetime.timedelta,
        if_not_found: Callable[[], T],
    ) -> T:
        func_cache = self.master_cache[funcname]
        cache_result: Optional[CacheEntry] = func_cache.get(args_key)
        now = datetime.datetime.now()
        if cache_result is None or cache_result['timestampt'] + time_delta < now or 'NO_CACHE' in os.environ:
            result = if_not_found()
            if result is None or not result:
                return result
            func_cache[args_key] = {
                'args_key': args_key,
                'timestampt': now,
                'result': result,
            }
            self.save()
        return func_cache[args_key]['result']


@functools.lru_cache(maxsize=1)
def _get_disk_cache() -> _DiskCache:
    return _DiskCache()


def disk_cache(  # type:ignore
    *,
    days: float = 0,
    seconds: float = 0,
    microseconds: float = 0,
    milliseconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    weeks: float = 0,
):
    time_delta = datetime.timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )

    def inner(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def __inner__(*args: P.args, **kwargs: P.kwargs) -> R:
            return _get_disk_cache().get_cached_result(
                funcname=func.__name__,
                args_key=f'args: {args}, kwargs: {kwargs}',
                time_delta=time_delta,
                if_not_found=lambda: func(*args, **kwargs),
            )
        return __inner__
    return inner


def view_pickle(pickle_file: str) -> None:
    """
    View a python pickle file.

    Mainly used to debug disk cache.
    """
    with open(pickle_file, 'rb') as f:
        print(json.dumps(pickle.load(f), indent=2, default=str))


def file_age_secs(filename: str) -> float:
    """
    Return how old a file is in seconds.
    """
    return time.time() - os.stat(filename).st_ctime


def file_is_recent(filename: str, time_delta: datetime.timedelta) -> bool:
    return file_age_secs(filename) < time_delta.total_seconds()


def file_is_old(filename: str, time_delta: datetime.timedelta) -> bool:
    return not file_is_recent(filename, time_delta)


# class CacheObject(TypedDict):
#     key: str
#     expiration_timestampt: int
#     value: Any


# def disk_cache(
#     days=0,
#     seconds=0,
#     microseconds=0,
#     milliseconds=0,
#     minutes=0,
#     hours=0,
#     weeks=0
# ):
#     def cached(func):
#         """
#         Decorator that caches the results of the function call.

#         We use Redis in this example, but any cache (e.g. memcached) will work.
#         We also assume that the result of the function can be seralized as JSON,
#         which obviously will be untrue in many situations. Tweak as needed.
#         """
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             # Generate the cache key from the function's arguments.
#             key_parts = [func.__name__] + list(args)
#             key = '-'.join(key_parts)
#             result = redis.get(key)

#             if result is None:
#                 # Run the function and cache the result for next time.
#                 value = func(*args, **kwargs)
#                 value_json = json.dumps(value)
#                 redis.set(key, value_json)
#             else:
#                 # Skip the function entirely and use the cached value instead.
#                 value_json = result.decode('utf-8')
#                 value = json.loads(value_json)

#             return value
#         return wrapper
#     return cached


# """An example of a cache decorator."""

# import json
# from functools import wraps
# from redis import StrictRedis


# redis = StrictRedis()

# def cached(func):
#     """
#     Decorator that caches the results of the function call.

#     We use Redis in this example, but any cache (e.g. memcached) will work.
#     We also assume that the result of the function can be seralized as JSON,
#     which obviously will be untrue in many situations. Tweak as needed.
#     """
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         # Generate the cache key from the function's arguments.
#         key_parts = [func.__name__] + list(args)
#         key = '-'.join(key_parts)
#         result = redis.get(key)

#         if result is None:
#             # Run the function and cache the result for next time.
#             value = func(*args, **kwargs)
#             value_json = json.dumps(value)
#             redis.set(key, value_json)
#         else:
#             # Skip the function entirely and use the cached value instead.
#             value_json = result.decode('utf-8')
#             value = json.loads(value_json)

#         return value
#     return wrapper

# # Usage:

# @cached
# def my_great_function():
#     # The below calculation will run the first time this function is called.
#     # On subsequent runs the result will be pulled from the cache instead.
#     return list(range(10000))
