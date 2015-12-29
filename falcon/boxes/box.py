# -*- encoding: utf-8 -*-

from abc import *


class MusicBox(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def notes(self):
        return

