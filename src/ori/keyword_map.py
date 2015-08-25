import redis
import sys
import msgpack

import libs


class KeywordMap(redis.StrictRedis):

    def __init__(self):
        conf = libs.get_config()
        host = conf.get('redis', 'host')
        port = conf.getint('redis', 'port')
        db_index = conf.getint('redis', 'db_index')
        self.__prefix = conf.get('redis', 'prefix')
        self.__super = super(KeywordMap, self)
        self.__super.__init__(host=host, port=port, db=db_index)

    def set(self, key, data):
        if data is None:
            return None
        value = msgpack.packb(data, use_bin_type=True)
        return self.__super.set(self.__prefix + key, value)

    def get(self, key):
        value = self.__super.get(self.__prefix + key)
        if value is not None:
            value = msgpack.unpackb(value)
        return value


if __name__ == '__main__':
    km = KeywordMap()
    for line in sys.stdin:
        line = line.strip()
        key, value = line.split("\t")
        print key, value, km.set(key, value)
