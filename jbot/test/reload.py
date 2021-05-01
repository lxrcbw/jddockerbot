from telethon import events
import importlib,os,sys
from .. import jdbot, chat_id, logger,_ConfigDir

@jdbot.on(events.NewMessage(chats=chat_id,pattern=r'^/reload'))
async def reload_modules(event):
    # botpath = _ConfigDir + "/jdbot/bot/"
    # diypath = _ConfigDir + "/jdbot/diy/"
    # logger.info('reloading bot module...')
    # reload_module('bot',botpath)
    # logger.info('reloading diy module...')
    # reload_module('diy',diypath)
    spec = importlib.util.spec_from_file_location('jdbot.bot.getcookie', '/jd/config/jdbot/bot/getcookie.py')
    load = importlib.util.module_from_spec(spec)
    importlib.reload(load)
def reload_module(module,path):
    files = os.listdir(path)
    for file in files:
        if file.endswith('.py'):
            filename = file.replace('.py', '')
            name = "jdbot.{}.{}".format(module, filename)
            spec = importlib.util.spec_from_file_location(name, path+file)
            load = importlib.util.module_from_spec(spec)
            # spec.loader.exec_module(load)
            importlib.reload(load)
            sys.modules[f"jdbot.{module}.{filename}"] = load
            print(sys.modules[f"jdbot.{module}.{filename}"])
            logger.info("JDBot加载 " + filename+" 完成")


