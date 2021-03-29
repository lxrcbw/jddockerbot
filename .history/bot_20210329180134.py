from telethon import TelegramClient, events,Button
import requests
import re
import json
import time
import os
import qrcode
from asyncio import exceptions
'''
TODO :
1、修改config.sh文件
2、修改定时文件 
'''
with open('/jd/config/bot.json') as f:
    bot = json.load(f)
chat_id = bot['user_id']
# 机器人 TOKEN
TOKEN = bot['bot_token']
# 发消息的TG代理
# my.telegram.org申请到的api_id,api_hash
api_id = bot['api_id']
api_hash = bot['api_hash']
proxy = (bot['proxy_type'], bot['proxy_add'], bot['proxy_port'])
# 开启tg对话
if proxy:
    client = TelegramClient('bot', api_id, api_hash,
                            proxy=proxy).start(bot_token=TOKEN)
else:
    client = TelegramClient('bot', api_id, api_hash).start(bot_token=TOKEN)

# 定义service.js访问
loginurl = "http://127.0.0.1:5678/auth"
codeurl = "http://127.0.0.1:5678/qrcode"
cookieurl = "http://127.0.0.1:5678/cookie"

date = {'username': '', 'password': ''}
img_file = '/jd/config/qr.jpg'
StartCMD = bot['StartCMD']

def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)


async def login():
    '''登录获取cookie，并进行替换'''
    session = requests.session()
    with open('/jd/config/auth.json') as f:
        res = json.load(f)
        date['username'] = res['user']
        date['password'] = res['password']
    flag = 160
    res = session.post(loginurl, data=date).json()
    res1 = session.get(codeurl).json()
    #print (res1)
    creatqr(res1['qrcode'])
    msg = await client.send_message(chat_id, "请扫码", file=img_file)
    while flag > 0:
        res2 = session.get(cookieurl).json()
        print(res2)
        if res2['err'] == 0:
            flag = 0
            # print(res2['cookie'])
            msg = await client.edit_message(msg, '已获取cookie,将自动替换\n'+res2['cookie'])
        time.sleep(1)
        flag -= 1
    if flag == 0:
        msg = await client.edit_message(msg, '超过时间未扫码，二维码已失效，请重新获取')
    elif flag == -1:
        print('-2')
        with open('/jd/config/config.sh', 'r+') as config:
            value = config.read()
            # print('config')
            #cookie = "pt_key=111225438435822555122;pt_pin=jd_HzvoWboKEyVF;"
            newvalue = await configup(res2['cookie'], value)
            # print('newvalue')
        if newvalue != value:
            # print('newvalue')
            with open('/jd/config/config.sh', 'w') as newconfig:
                newconfig.write(newvalue)
                await client.edit_message(msg, '已完成替换并保存文件')


def creatqr(text):
    '''实例化QRCode生成qr对象'''
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.clear()
    # 传入数据
    qr.add_data(text)
    qr.make(fit=True)
    # 生成二维码
    img = qr.make_image()
    # 保存二维码
    img.save(img_file)


async def configup(cookie, value):
    '''替换修改config文件cookie'''
    pinReg = re.compile(r'pt_pin=[\S]+;')
    pin = re.findall(pinReg, cookie)[0]
    # print(pin)
    cookiereg = re.compile(r'pt_key=[\S]+;'+pin)
    # print(cookiereg)
    oldcookie = re.findall(cookiereg, value)[0]
    # print(oldcookie)
    if oldcookie:
        # print('oldcookie')
        newvalue = value.replace(oldcookie, cookie)
        return newvalue
    else:
        await client.send_message(chat_id, '未找到匹配cookie，替换失败')
        # print('else')
        return value

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
async def logbtn(conv,SENDER, path: str, content: str,msg):
    '''定义log日志按钮'''
    try:
        dir = os.listdir(path)
        markup = [Button.inline(file, data=str(path+'/'+file))
                for file in dir]
        markup.append(Button.inline('取消', data='cancle'))
        markup = split_list(markup, 3)
        msg = await client.edit_message(msg,'请做出你的选择：', buttons=markup)
        date = await conv.wait_event(press_event(SENDER))
        res = bytes.decode(date.data)
        if res == 'cancle':
            msg = await client.edit_message(msg,'对话已取消')
            conv.cancel()
            return None,None
        elif os.path.isfile(res):
            msg = await client.edit_message(msg, content + '中，请注意查收')
            await conv.send_file(res)
            msg = await client.edit_message(msg, content + '成功，请查收')
            conv.cancel()
            return None,None
        else:
            return res,msg
    except exceptions.TimeoutError:
        msg = await client.edit_message(msg,'选择已超时，对话已停止')
        return None,None
    except :
        msg = await client.edit_message(msg,'something wrong,I\'m sorry')
        return None,None

async def nodebtn(conv,SENDER, path: str, msg):
    '''定义scripts脚本按钮'''
    try:
        dir = os.listdir(path)
        markup = [Button.inline(file, data=str(path+'/'+file))
                for file in dir]
        markup.append(Button.inline('取消', data='cancel'))
        markup = split_list(markup, 3)
        msg = await client.edit_message(msg,'请做出你的选择：', buttons=markup)
        date = await conv.wait_event(press_event(SENDER))
        res = bytes.decode(date.data)
        if res == 'cancel':
            msg = await client.edit_message(msg,'对话已取消')
            conv.cancel()
            return None,None
        elif os.path.isfile(res):
            msg = await client.edit_message(msg, '脚本即将在后台运行')
            res = res.split('/')[-1]
            print(res)
            #log = time.strftime("%Y-%m-%d-%H-%M-%S")+'.log'
            os.popen('nohup bash jd {} now >/jd/log/bot.log &'.format(res))
            msg = await client.edit_message(msg, res +'在后台运行成功，请自行在程序结束后查看日志')
            conv.cancel()
            return None,None
        else:
            return res,msg
    except exceptions.TimeoutError:
        msg = await client.edit_message(msg,'选择已超时，对话已停止')
        return None,None
    except :
        msg = await client.edit_message(msg,'something wrong,I\'m sorry')
        return None,None

@client.on(events.NewMessage(from_users=chat_id, pattern=r'^/log'))
async def mylog(event):
    # 定义日志操作
    SENDER = event.sender_id
    path = '/jd/log'
    async with client.conversation(SENDER, timeout=30) as conv:
        msg = await conv.send_message('正在查询，请稍后')
        while path:
            path,msg = await logbtn(conv,SENDER, path,'查询日志', msg)

@client.on(events.NewMessage(from_users=chat_id, pattern=r'^/snode'))
async def mysnode(event):
    SENDER = event.sender_id
    path = '/jd/scripts'
    async with client.conversation(SENDER, timeout=30) as conv:
        msg = await conv.send_message('正在查询，请稍后')
        while path:
            path,msg = await nodebtn(conv,SENDER, path,msg)

@client.on(events.NewMessage(from_users=chat_id))
async def myfile(event):
    '''定义文件操作'''
    if event.message.file:
        if event.message.file.name == 'config.sh' or event.message.file.name == 'crontab.list':
            path = '/jd/config/'
        else:
            path = '/jd/scripts/'
        if os.path.exists(path+event.message.file.name):
            try:
                os.rename(path+event.message.file.name,path+event.message.file.name+'.bak')
            except WindowsError:
                os.remove(path+event.message.file.name+'.bak')
                os.rename(path+event.message.file.name,path+event.message.file.name+'.bak')
        await client.download_media(event.message, path)
        msg = await client.send_message(chat_id, '已保存到'+path+'文件夹')
        if event.message.file.name == 'crontab.list':
            os.popen('crontab '+path+event.message.file.name)
            await client.edit_message(msg,'定时文件已更新')

@client.on(events.NewMessage(from_users=918498266, pattern='/bash'))
async def mybash(event):
    '''接收/bash命令后执行程序'''
    bashreg = re.compile(r'^/bash [\S]+')
    text = re.findall(bashreg, event.raw_text)
    if len(text) == 0:
        res = '''请正确使用/bash命令，例如
        /bash jd 获取jd脚本名称
        /bash git_pull 更新脚本文件
        /bash diy 更新DIY文件
        /bash /abc/cde.sh 运行abc目录下的cde.sh文件
        '''
        await client.send_message(chat_id, res)
    else:
        await cmd('bash '+text[0].replace('/bash ', ''))

@client.on(events.NewMessage(from_users=chat_id, pattern='/node'))
async def mynode(event):
    '''接收/node命令后执行程序'''
    nodereg = re.compile(r'^/node [\S]+')
    text = re.findall(nodereg, event.raw_text)
    if len(text) == 0:
        res = '''请正确使用/node命令，如
        /node jd_bean_change 运行jd_bean_change脚本
        /node jd_jdzz 运行jd_jdzz脚本
        /node jd_XXX 运行jd_XXX脚本
        '''
        await client.send_message(chat_id, res)
    else:
        await cmd('bash jd '+text[0].replace('/node ', '')+' now')


@client.on(events.NewMessage(from_users=chat_id, pattern='/cmd'))
async def mycmd(event):
    '''接收/cmd命令后执行程序'''
    if StartCMD:
        cmdreg = re.compile(r'^/cmd [\s\S]+')
        text = re.findall(cmdreg, event.raw_text)
        if len(text) == 0:
            msg = '''请正确使用/cmd命令，如
            /cmd python3 /python/bot.py 运行/python目录下的bot文件
            /cmd ps 获取当前docker内进行
            /cmd kill -9 1234 立即杀死1234进程
            '''
            await client.send_message(chat_id, msg)
        else:
            print(text)
            await cmd(text[0].replace('/cmd ', ''))
    else:
        await client.send_message(chat_id, '未开启CMD命令，如需使用请修改配置文件')


async def cmd(cmdtext):
    '''定义执行cmd命令'''
    try:
        await client.send_message(chat_id, '开始执行程序，如程序复杂，建议稍等')
        res = os.popen(cmdtext).read()
        await client.send_message(chat_id, res)
    except:
        await client.send_message(chat_id, '执行出错，请检查命令是否正确')


@client.on(events.NewMessage(from_users=chat_id, pattern=r'^/getcookie'))
async def mycookie(event):
    '''接收/getcookie后执行程序'''
    await login()


@client.on(events.NewMessage(from_users=chat_id, pattern='/help'))
async def myhelp(event):
    '''接收/help /start命令后执行程序'''
    msg = '''使用方法如下：
    /start 开始使用本程序
    /help 查看使用帮助
    /bash 执行bash程序，如git_pull、diy及可执行自定义.sh，例如/bash /jd/config/abcd.sh
    /node 执行js脚本文件，目前仅支持/scirpts、/config目录下js，直接输入/node jd_bean_change 即可进行执行。该命令会等待脚本执行完，期间不能使用机器人，建议使用snode命令。
    /cmd 执行cmd命令,例如/cmd python3 /python/bot.py 则将执行python目录下的bot.py
    /snode 命令可以选择脚本执行，只能选择/jd/scripts目录下的脚本，选择完后直接后台运行，不影响机器人响应其他命令
    /log 选择查看执行日志
    此外直接发送文件，将自动保存至/jd/scripts/或/jd/config目录下，如果是config.sh，crontab.list会覆盖原文件，crontab.list文件会自动更新时间;其他文件会被保存到/jd/scripts文件夹下'''
    await client.send_message(chat_id, msg)


@client.on(events.NewMessage(from_users=chat_id, pattern='/start'))
async def mystart(event):
    '''接收/help /start命令后执行程序'''
    msg = '''使用方法如下：
    /start 开始使用本程序
    /help 查看使用帮助
    /bash 执行bash程序，如git_pull、diy及可执行自定义.sh，例如/bash /jd/config/abcd.sh
    /node 执行js脚本文件，目前仅支持/scirpts、/config目录下js，直接输入/node jd_bean_change 即可进行执行。该命令会等待脚本执行完，期间不能使用机器人，建议使用snode命令。
    /cmd 执行cmd命令,例如/cmd python3 /python/bot.py 则将执行python目录下的bot.py
    /snode 命令可以选择脚本执行，只能选择/jd/scripts目录下的脚本，选择完后直接后台运行，不影响机器人响应其他命令
    /log 选择查看执行日志
    此外直接发送文件，将自动保存至/jd/scripts/或/jd/config目录下，如果是config.sh，crontab.list会覆盖原文件，crontab.list文件会自动更新时间;其他文件会被保存到/jd/scripts文件夹下'''
    await client.send_message(chat_id, msg)

with client:
    client.loop.run_forever()
