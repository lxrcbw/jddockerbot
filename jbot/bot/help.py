from telethon import events
from .. import jdbot, chat_id


@jdbot.on(events.NewMessage(from_users=chat_id, pattern='/help'))
async def myhelp(event):
    '''接收/help命令后执行程序'''
    msg = '''
    a-我的自定义快捷按钮
    edit-编辑文件
    start-开始使用本程序
    node-执行js脚本文件，绝对路径。
    cmd-执行cmd命令
    snode-选择脚本后台运行
    log-选择日志
    getfile-获取jd目录下文件
    setshort-设置自定义按钮
    getcookie-扫码获取cookie'''
    await jdbot.send_message(chat_id, msg)
