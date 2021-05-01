#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# 0.3 版本开始不再区分ql、V3、V4。运行日志：log/bot/run.log
# author：   https://github.com/SuMaiKaDe

from . import jdbot, chat_id, logger, newloop, _JdbotDir, _LogDir
from .utils import load_diy, new_loop
import threading
import os
version = 'version:0.3'
botlog = '''
2021年4月30日
    **为您带来全新的0.3版本**
    1、 重构文件，新增支持自定义功能（欢迎各路大佬PR）
        将你的py文件放在/jd/jbot/diy下，重启机器人自动添加
    2、 新增支持后台运行完发送文件，使用BOTAPI方式，自建反代，每天10W次额度。
        我很菜，搞不定协程与线程的处理，所以只能采用这种方式了
        针对上述反代，我自己账号申请的，免费的。大家也可以申请，后续看情况改
    3、 新增/edit 与/getfile 参数支持
        - 例如/edit /jd/config/bot.json，则直接编辑bot.json
        - 例如/getfile /jd/config 则进入config选择文件
    4、 每次有更新会发送通知
    5、 新增/bean功能
        - /bean 加数字则返回该账户的近日收支
        - /bean in\out显示所有账户近日收、支
        - /bean 显示所有账户京豆总量
    6、 尝试不再区分V4，V3与青龙，加入了判断，如不能使用，请及时联系我
'''
_botuplog = _LogDir + '/bot/up.log'
botpath = _JdbotDir + "/bot/"
diypath = _JdbotDir + "/diy/"
logger.info('loading bot module...')
load_diy('bot', botpath)
logger.info('loading diy module...')
load_diy('diy', diypath)


async def hello():
    if os.path.exists(_botuplog):
        isnew = False
        with open(_botuplog, 'r', encoding='utf-8') as f:
            logs = f.readlines()
        for log in logs:
            if version in log:
                isnew = True
                return
        if not isnew:
            with open(_botuplog, 'a', encoding='utf-8') as f:
                f.writelines([version, botlog])
            await jdbot.send_message(chat_id, '[机器人上新了](https://github.com/SuMaiKaDe/jddockerbot/tree/master)\n'+botlog, link_preview=False)
    else:
        with open(_botuplog, 'w+', encoding='utf-8') as f:
            f.writelines([version, botlog])
        await jdbot.send_message(chat_id, '[机器人上新了](https://github.com/SuMaiKaDe/jddockerbot/tree/master)\n'+botlog, link_preview=False)
if __name__ == "__main__":
    with jdbot:
        jdbot.loop.create_task(hello())
        threading.Thread(target=new_loop, args=(newloop,)).start()
        jdbot.loop.run_forever()
