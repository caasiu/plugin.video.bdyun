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
        'label': u'## 搜索视频或音频',
        'path': plugin.url_for('search'),
        'is_playable': False
        }]
        pcs_files = pcs.list_dir_all(user_info['cookie'], user_info['tokens'], path='/')
        item_list = mk_list(pcs_files)
        items.extend(item_list)
    return plugin.finish(items, update_listing=True)


@plugin.route('/login_dialog/')
def login_dialog():
    username = dialog.input(u'用户名:', type=xbmcgui.INPUT_ALPHANUM)
    password = dialog.input(u'密码:', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if username and password:
        cookie,tokens = get_auth.run(username,password)
        if tokens:
            save_user_info(username,password,cookie,tokens)
            dialog.ok('',u'登录成功',u'如没有自动转跳，请重新进入该插件')
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
    if key:
        s = pcs.search(user_cookie, user_tokens, key)
        items = []
        if len(s['list']) == 1:
            for result in s['list']:
                if result['category'] == 1 or result['category'] == 2:
                    if 'thumbs' in result and 'url2' in result['thumbs']:   
                        ThumbPath = result['thumbs']['url2']
                        item = {
                                'label': result['server_filename'],
                                #'path': plugin.url_for('login_dialog'),
                                'is_playable': True, 
                                'icon': ThumbPath,
                                }
                    else:
                        item = {
                                'label': result['server_filename'],
                                #'path': plugin.url_for('login_dialog'),
                                'is_playable': True,
                                }
                    items.append(item)
            if items:
                return plugin.finish(items)
            else:
                dialog.ok('',u'搜素的文件不是视频或音频')

        elif s['list']:
            for result in s['list']:
                if result['category'] == 1 or result['category'] == 2:
                    if 'thumbs' in result and 'url2' in result['thumbs']:   
                        ThumbPath = result['thumbs']['url2']
                        item = {
                                'label': result['server_filename'],
                                #'path': plugin.url_for('login_dialog'),
                                'is_playable': True, 
                                'icon': ThumbPath,
                                }
                    else:
                        item = {
                                'label': result['server_filename'],
                                #'path': plugin.url_for('login_dialog'),
                                'is_playable': True,
                                }
                    items.append(item)
            if items:
                return plugin.finish(items)
            else:
                dialog.ok('',u'搜素的文件不是视频或音频')

        else:
            dialog.ok('',u'没有找到文件')
            return None

    return 


@plugin.route('/directory/<path>')
def directory(path):
    user_info = get_user_info()
    user_cookie = user_info['cookie']
    user_tokens = user_info['tokens']
    dir_files = pcs.list_dir_all(user_info['cookie'], user_info['tokens'], path.decode('utf-8'))
    item_list = mk_list(dir_files)

    previous_path = os.path.dirname(path)
    if previous_path == '/':
        item_list.insert(0,{
                'label': u'返回首页',
                'path': plugin.url_for('main_menu')
            })
    else:
        item_list.insert(0,{
                'label': u'<< 返回上一层',
                'path': plugin.url_for('directory', path=previous_path),
            })

    return plugin.finish(item_list, update_listing=True)


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


def mk_list(pcs_files):
    item_list = []
    for result in pcs_files:
        if result['isdir'] == 1:
            item = {
                    'label': result['server_filename'],
                    'path': plugin.url_for('directory', path=result['path'].encode('utf-8')),
                    'is_playable': False 
                    }
            item_list.append(item)
        elif result['category'] == 1 or result['category'] == 2:
            if 'thumbs' in result and 'url2' in result['thumbs']:   
                ThumbPath = result['thumbs']['url2']
                item = {
                        'label': result['server_filename'],
                        #'path': plugin.url_for('login_dialog'),
                        'is_playable': True, 
                        'icon': ThumbPath,
                        }
            else:
                item = {
                        'label': result['server_filename'],
                        #'path': plugin.url_for('login_dialog'),
                        'is_playable': True,
                        }
            item_list.append(item)
    return item_list
    


if __name__ == '__main__':
    plugin.run()


