import redis
import ConfigParser
import sys


class KeywordMap(redis.StrictRedis):

    def __init__(self, config):
        host = config.get('redis', 'host')
        port = config.getint('redis', 'port')
        db_index = config.getint('redis', 'db_index')
        super(KeywordMap, self).__init__(host=host, port=port, db=db_index)


if __name__ == '__main__':
    def __init_config(config_file='conf/server.cfg'):
        if len(sys.argv) > 1:
            config_file = sys.argv[1]

        config = ConfigParser.ConfigParser()
        config.read(config_file)

        return config

    config = __init_config()

    km = KeywordMap(config)
    for line in sys.stdin:
        line = line.strip()
        key, value = line.split("\t")
        print km.set(key, 'int_cat_40150110160')
