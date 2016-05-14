#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc

try:
    import ChineseKeyboard as _xbmc
    #kb = ChineseKeyboard.Keyboard()
except ImportError as e:
    import xbmc as _xbmc
    #kb = xbmc.Keyboard()


def keyboard(default='', heading='', hidden=False):
    #_kb.setDefault(default)
    #_kb.setHeading(heading)
    #_kb.setHiddenInput(hidden)
    kb = _xbmc.Keyboard(default,heading)
    kb.doModal()
    if kb.isConfirmed():
        text = kb.getText()
        return unicode(text, 'utf-8')
