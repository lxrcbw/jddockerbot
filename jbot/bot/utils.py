import os
from telethon import events, Button
import re
import requests
from .. import jdbot, chat_id, _LogDir, logger, _JdDir,_DiyScripts,_OwnDir,TOKEN,newloop,proxystart
import asyncio
import subprocess
import datetime

if os.environ['JD_DIR']:
    _DiyDir = _OwnDir
    jdcmd = 'jtask'
elif os.environ['QL_DIR']:
    _DiyDir = _DiyScripts
    jdcmd = 'js'
else:
    _DiyDir = None
    jdcmd = 'node'


def split_list(datas, n, row: bool = True):
    """一维列表转二维列表，根据N不同，生成不同级别的列表"""
    length = len(datas)
    size = length / n + 1 if length % n else length/n
    _datas = []
    if not row:
        size, n = n, size
    for i in range(int(size)):
        start = int(i * n)
        end = int((i + 1) * n)
        _datas.append(datas[start:end])
    return _datas


async def backfile(file):
    '''如果文件存在，则备份，并更新'''
    if os.path.exists(file):
        try:
            os.rename(file, file+'.bak')
        except WindowsError:
            os.remove(file+'.bak')
            os.rename(file, file+'.bak')


def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)


async def cmd(cmdtext):
    '''定义执行cmd命令'''
    try:
        msg = await jdbot.send_message(chat_id, '开始执行程序，如程序复杂，建议稍等')
        res_bytes = subprocess.check_output(
            cmdtext, shell=True, stderr=subprocess.STDOUT)
        res = res_bytes.decode('utf-8')
        if len(res) == 0:
            await jdbot.edit_message(msg, '已执行，但返回值为空')
        elif len(res) <= 4000:
            await jdbot.edit_message(msg, res)
        elif len(res) > 4000:
            with open(_LogDir+'/botres.log', 'w+', encoding='utf-8') as f:
                f.write(res)
            await jdbot.send_message(chat_id, '执行结果较长，请查看日志', file=_LogDir+'/botres.log')
    except Exception as e:
        await jdbot.send_message(chat_id, 'something wrong,I\'m sorry\n'+str(e))
        logger.error('something wrong,I\'m sorry'+str(e))


async def getname(path, dir):
    '''获取文件中文名称，如无则返回文件名'''
    names = []
    reg = r'new Env\(\'[\S]+?\'\)'
    cname = False
    for file in dir:
        if os.path.isdir(path+'/'+file):
            names.append(file)
        elif file.endswith('.js') and file != 'jdCookie.js' and file != 'getJDCookie.js' and file != 'JD_extra_cookie.js' and 'ShareCode' not in file:
            with open(path+'/'+file, 'r', encoding='utf-8') as f:
                resdatas = f.readlines()
            for data in resdatas:
                if 'new Env' in data:
                    data = data.replace('\"', '\'')
                    res = re.findall(reg, data)
                    if len(res) != 0:
                        res = res[0].split('\'')[-2]
                        names.append(res+'--->'+file)
                        cname = True
                    break
            if not cname:
                names.append(file+'--->'+file)
                cname = False
        else:
            continue
    return names


async def logbtn(conv, SENDER, path, msg, page, filelist):
    '''定义log日志按钮'''
    mybtn = [Button.inline('上一页', data='up'), Button.inline(
        '下一页', data='next'), Button.inline('上级', data='updir'), Button.inline('取消', data='cancel')]
    try:
        if filelist:
            markup = filelist
            newmarkup = markup[page]
            if mybtn not in newmarkup:
                newmarkup.append(mybtn)
        else:
            dir = os.listdir(path)
            dir.sort()
            markup = [Button.inline(file, data=str(file))
                      for file in dir]
            markup = split_list(markup, 3)
            if len(markup) > 30:
                markup = split_list(markup, 30)
                newmarkup = markup[page]
                newmarkup.append(mybtn)
            else:
                newmarkup = markup
                if path == _JdDir:
                    newmarkup.append([Button.inline('取消', data='cancel')])
                else:
                    newmarkup.append(
                        [Button.inline('上级', data='updir'), Button.inline('取消', data='cancel')])
        msg = await jdbot.edit_message(msg, '请做出您的选择：', buttons=newmarkup)
        convdata = await conv.wait_event(press_event(SENDER))
        res = bytes.decode(convdata.data)
        if res == 'cancel':
            msg = await jdbot.edit_message(msg, '对话已取消')
            conv.cancel()
            return None, None, None, None
        elif res == 'next':
            page = page + 1
            if page > len(markup) - 1:
                page = 0
            return path, msg, page, markup
        elif res == 'up':
            page = page - 1
            if page < 0:
                page = len(markup) - 1
            return path, msg, page, markup
        elif res == 'updir':
            path = '/'.join(path.split('/')[:-1])
            logger.info(path)
            if path == '':
                path = _JdDir
            return path, msg, page, None
        elif os.path.isfile(path+'/'+res):
            msg = await jdbot.edit_message(msg, '文件发送中，请注意查收')
            await conv.send_file(path+'/'+res)
            msg = await jdbot.edit_message(msg, res+'发送成功，请查收')
            conv.cancel()
            return None, None, None, None
        else:
            return path+'/'+res, msg, page, None
    except asyncio.exceptions.TimeoutError:
        msg = await jdbot.edit_message(msg, '选择已超时，本次对话已停止')
        return None, None, None, None
    except Exception as e:
        msg = await jdbot.edit_message(msg, 'something wrong,I\'m sorry\n'+str(e))
        logger.error('something wrong,I\'m sorry\n'+str(e))
        return None, None, None, None


async def nodebtn(conv, SENDER, path, msg, page, filelist):
    '''定义scripts脚本按钮'''
    mybtn = [Button.inline('上一页', data='up'), Button.inline(
        '下一页', data='next'), Button.inline('上级', data='updir'), Button.inline('取消', data='cancel')]
    try:
        if filelist:
            markup = filelist
            newmarkup = markup[page]
            if mybtn not in newmarkup:
                newmarkup.append(mybtn)
        else:
            if path == _JdDir:
                dir = ['scripts', _DiyDir.split('/')[-1]]
            else:
                dir = os.listdir(path)
                dir = await getname(path, dir)
            dir.sort()
            markup = [Button.inline(file.split('--->')[0], data=str(file.split('--->')[-1]))
                      for file in dir if os.path.isdir(path+'/'+file) or file.endswith('.js')]
            markup = split_list(markup, 3)
            if len(markup) > 30:
                markup = split_list(markup, 30)
                newmarkup = markup[page]
                newmarkup.append(mybtn)
            else:
                newmarkup = markup
                if path == _JdDir:
                    newmarkup.append([Button.inline('取消', data='cancel')])
                else:
                    newmarkup.append(
                        [Button.inline('上级', data='updir'), Button.inline('取消', data='cancel')])
        msg = await jdbot.edit_message(msg, '请做出您的选择：', buttons=newmarkup)
        convdata = await conv.wait_event(press_event(SENDER))
        res = bytes.decode(convdata.data)
        if res == 'cancel':
            msg = await jdbot.edit_message(msg, '对话已取消')
            conv.cancel()
            return None, None, None, None
        elif res == 'next':
            page = page + 1
            if page > len(markup) - 1:
                page = 0
            return path, msg, page, markup
        elif res == 'up':
            page = page - 1
            if page < 0:
                page = len(markup) - 1
            return path, msg, page, markup
        elif res == 'updir':
            path = '/'.join(path.split('/')[:-1])
            if path == '':
                path = _JdDir
            return path, msg, page, None
        elif os.path.isfile(path+'/'+res):
            conv.cancel()
            msg = await jdbot.edit_message(msg, '脚本即将在后台运行')
            logger.info(path+'/'+res+'脚本即将在后台运行')
            cmdtext = '{} {}/{} now'.format(jdcmd,path, res)
            asyncio.run_coroutine_threadsafe(backcmd(cmdtext),newloop)
            msg = await jdbot.edit_message(msg, res + '在后台运行成功，请自行在程序结束后查看日志')
            return None, None, None, None
        else:
            return path+'/'+res, msg, page, None
    except asyncio.exceptions.TimeoutError:
        msg = await jdbot.edit_message(msg, '选择已超时，对话已停止')
        return None, None, None, None
    except Exception as e:
        msg = await jdbot.edit_message(msg, 'something wrong,I\'m sorry\n'+str(e))
        logger.error('something wrong,I\'m sorry\n'+str(e))
        return None, None, None, None

def send_file(chatid,file):
    # if HOSTAPI:
    #     url = f'https://{HOSTAPI}/bot{TOKEN}/sendDocument?chat_id={chatid}'
    if proxystart :
        url = f'https://a.jdtgbot.workers.dev/bot{TOKEN}/sendDocument?chat_id={chatid}'
    else:
        url = f'https://api.telegram.org/bot{TOKEN}/sendDocument?chat_id={chatid}'
    files = {'document': open(file, 'rb')}
    requests.post(url,files=files)

async def backcmd(cmdtext):
    _log = _LogDir + '/bot/'+cmdtext.split('/')[-1].split('.js')[0]+datetime.datetime.now().strftime('%H-%M-%S')+'.log'
    res_bytes = subprocess.check_output(
        cmdtext, shell=True, stderr=subprocess.STDOUT)
    res = res_bytes.decode('utf-8')
    with open(_log, 'w+', encoding='utf-8') as f:
        f.write(res)
    send_file(chat_id,_log)
    os.remove(_log)