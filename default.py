#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import os, sys, re, json 

from lib.resource import get_auth
from lib.resource import pcs
from xbmcswift2 import Plugin

plugin = Plugin()
dialog = xbmcgui.Dialog()


@plugin.route('/')
def main_menu():
    user_info = get_user_info()
    if user_info is None:
        items = [{
        'label': u'登入',
        'path': plugin.url_for('login_dialog'),
        'is_playable': False
        }]
    else:
        pcs_info = pcs.get_pcs_info(user_info['cookie'], user_info['tokens'])
        items = [{
        'label': u'## 当前帐号: %s' %user_info['username'],
        'path': plugin.url_for('accout_setting'),
        'is_playable': False,
        'icon': pcs_info['avatar_url']
        },{
        'label': u'## 搜索',
        'path': plugin.url_for('search'),
        'is_playable': False
        }]
    return plugin.finish(items , update_listing=True)


@plugin.route('/login_dialog/')
def login_dialog():
    username = dialog.input('username:', type=xbmcgui.INPUT_ALPHANUM)
    password = dialog.input('password:', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if username and password:
        cookie,tokens = get_auth.run(username,password)
        if tokens:
            save_user_info(username,password,cookie,tokens)
            dialog.ok('',u'登录成功')
            return None
    else:
        dialog.ok('Error',u'用户名或密码不能为空')
    return None


@plugin.route('/accout_setting/')
def accout_setting():
    user_info = get_user_info()
    items = [{
    'label': u'登出和清除缓存',
    'path': plugin.url_for('clear_cache'),
    'is_playable': False
    },{
    'label': 'relogin',
    'is_playable': False
    },{
    'label': 'setting',
    'is_playable': False
    }]
    if user_info:
        return plugin.finish(items)
    else:
        return


@plugin.route('/accout_setting/clear_cache/')
def clear_cache():
    info = plugin.get_storage('info')
    info.clear()
    dialog.ok('',u'清理完毕')
    return


@plugin.route('/search/')
def search():
    user_info = get_user_info()
    user_cookie = user_info['cookie']
    user_tokens = user_info['tokens']
    key = dialog.input(u'输入文件名/关键词', type=xbmcgui.INPUT_ALPHANUM)
    s = pcs.search(user_cookie, user_tokens, key)
    items = []
    if len(s['list']) == 1:
        for result in s['list']:
            if result['category'] == 1 or result['category'] == 2:
                item = {
                        'label': result['server_filename'],
                        #'path': plugin.url_for('login_dialog'),
                        'is_playable': False 
                       }
                items.append(item)
        if items:
            return plugin.finish(items)
        else:
            dialog.ok('',u'搜素的文件不是视频或音频')

    elif s['list']:
        for result in s['list']:
            if result['category'] == 1 or result['category'] == 2:
                item = {
                        'label': result['path'],
                        #'path': plugin.url_for('login_dialog'),
                        'is_playable': False
                       }
                items.append(item)
        if items:
            return plugin.finish(items)
        else:
            dialog.ok('',u'搜素的文件不是视频或音频')

    else:
        dialog.ok('',u'没有找到文件')

    return None


def get_user_info():
    info = plugin.get_storage('info')
    user_info = info.get('user_info')
    return user_info


def save_user_info(username, password, cookie, tokens):
    info = plugin.get_storage('info')
    user_info = info.setdefault('user_info',{})
    user_info['username'] = username
    user_info['password'] = password
    user_info['cookie'] = cookie
    user_info['tokens'] = tokens
    info.sync()


if __name__ == '__main__':
    plugin.run()


