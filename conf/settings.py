import configparser
import io
import os
import logging.config
import logging

ENV = os.getenv("REPORT_ENV", 'dev')
#CONFIG_FILE_PATH = './conf/config.properties'
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.properties')  # for debug environment

FILE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'a3.txt')


def read_list(file):
    """Return file as list if exists
    """
    l = []
    if os.path.exists(file):
        with open(file) as f:
            l.extend(f.read().splitlines())
    else:
        logging.debug('%s not found' % file)
    return l


class Settings:
    config_file_path = CONFIG_FILE_PATH
    config = configparser.ConfigParser()
    config.readfp(io.open(config_file_path, encoding="utf8"))
    env = os.getenv("REPORT_ENV", 'dev')

    def __init__(self, env=ENV):
        self.env = env

    def __getitem__(self, item):
        return self.config.get(self.env, item)

settings = Settings()
A3_LIST = read_list(FILE_CONFIG_PATH)
