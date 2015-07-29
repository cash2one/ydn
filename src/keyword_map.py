import redis
import sys

import libs


class KeywordMap(redis.StrictRedis):

    def __init__(self):
        config = libs.get_config()
        host = config.get('redis', 'host')
        port = config.getint('redis', 'port')
        db_index = config.getint('redis', 'db_index')
        self.__prefix = config.get('redis', 'prefix')
        self.__super = super(KeywordMap, self)
        self.__super.__init__(host=host, port=port, db=db_index)

    def set(self, key, value):
        return self.__super.set(self.__prefix + key, value)

    def get(self, key):
        return self.__super.get(self.__prefix + key)


if __name__ == '__main__':
    config = libs.get_config()
    km = KeywordMap(config)
    for line in sys.stdin:
        line = line.strip()
        key, value = line.split("\t")
        print km.set(key, value)
