import os

from configparser import ConfigParser

SECTION_CFG = 'config'
CFG_NAME = 'ovd.ini'

DIR = 'save_dir'
NUM = 'thread_num'


def write_cfg():
    cfg.write(open(CFG_NAME, 'w', encoding='utf8'))


def get_dir():
    return cfg.get(SECTION_CFG, DIR)


def get_num():
    return cfg.getint(SECTION_CFG, NUM)


def set_item(key, value):
    if key == DIR:
        value = value.replace('\\', '/')
    cfg.set(SECTION_CFG, key, str(value))
    write_cfg()


def init_cfg():
    cfg.add_section(SECTION_CFG)
    cfg.set(SECTION_CFG, DIR, '')
    cfg.set(SECTION_CFG, NUM, '8')
    write_cfg()


cfg = ConfigParser()
if not os.path.exists(CFG_NAME):
    init_cfg()
cfg.read(CFG_NAME)
