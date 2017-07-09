# -*- coding: utf-8 -*-
import staticconf


CONFIG_NS = 'moneybot'

config = staticconf.NamespaceReaders(CONFIG_NS)


def load_config(path):
    staticconf.YamlConfiguration(path, namespace=CONFIG_NS)
