import time
import datetime
import random
import os
from functools import wraps
from django.db.models import CharField, ForeignKey, BigAutoField


twepoch = 1609459200000  # 2021-01-01 00:00:00+00:00 UTC
worker_id_bits = 5
process_id_bits = 5
increment_id_bits = 12
max_worker_id = 1 << worker_id_bits
max_process_id = 1 << process_id_bits
max_increment_id = 1 << increment_id_bits
max_timestamp = 1 << (64 - worker_id_bits - process_id_bits - increment_id_bits)


def make_snowflake(timestamp_ms, worker_id, process_id, increment_id, twepoch=twepoch):
    """generate a twitter-snowflake id, based on
    https://github.com/twitter/snowflake/blob/master/src/main/scala/com/twitter/service/snowflake/IdWorker.scala
    :param: timestamp_ms time since UNIX epoch in milliseconds"""

    sid = ((int(timestamp_ms) - twepoch) % max_timestamp) << worker_id_bits << process_id_bits << increment_id_bits
    sid += (worker_id % max_worker_id) << process_id_bits << increment_id_bits
    sid += (process_id % max_process_id) << increment_id_bits
    sid += increment_id % max_increment_id

    return str(sid)


def snowflake_to_time(snowflake):
    # From https://github.com/vegeta897/snow-stamp/blob/main/src/convert.js
    return datetime.datetime.fromtimestamp(float(int(snowflake) / 4194304000 + twepoch / 1000))


def id_seq_cache(func):
    prefix_cache = {}
    timestamp_ms = int(time.time() * 1000)

    @wraps(func)
    def new_id(prefix='', increment_id=0):
        nonlocal timestamp_ms
        nonlocal prefix_cache
        new_timestamp_ms = int(time.time() * 1000)
        if prefix not in prefix_cache:
            prefix_cache[prefix] = 0
        else:
            if new_timestamp_ms == timestamp_ms:
                prefix_cache[prefix] = (prefix_cache[prefix] + 1) % max_increment_id
            else:
                prefix_cache[prefix] = increment_id % max_increment_id
                timestamp_ms = new_timestamp_ms
        return func(prefix, prefix_cache[prefix])

    new_id._prefix_cache = prefix_cache
    return new_id


@id_seq_cache
def gen_new_id(prefix='', increment_id=0):
    snowflake = make_snowflake(int(time.time()*1000), random.randint(0, 31), os.getpid(), increment_id)
    return "%s%s" % (prefix, snowflake)


class TableNamePKField(CharField):

    def auto_id(self):
        return gen_new_id(self._prefix)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['blank']
        del kwargs['default']
        del kwargs['max_length']
        del kwargs['editable']
        del kwargs['primary_key']
        args = (self._prefix,)
        return name, path, args, kwargs

    def __init__(self, prefix='', *args, **kwargs):
        self._last_timestamp = time.time()
        self._seq_id = 0
        if len(prefix) > 10:
            raise AttributeError('prefix > 10 !')
        self._prefix = prefix
        args = []
        kwargs['max_length'] = 32
        kwargs['blank'] = True
        kwargs['null'] = False
        kwargs['primary_key'] = True
        kwargs['editable'] = False
        kwargs['default'] = self.auto_id
        super().__init__(*args, **kwargs)
