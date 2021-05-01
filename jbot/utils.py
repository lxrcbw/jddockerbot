import sys
import importlib
import os
from . import logger
import asyncio


def load_diy(module, path):
    files = os.listdir(path)
    for file in files:
        if file.endswith('.py'):
            filename = file.replace('.py', '')
            name = "jbot.{}.{}".format(module, filename)
            spec = importlib.util.spec_from_file_location(name, path+file)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules[f"jbot.{module}.{filename}"] = load
            logger.info("JBot加载 " + filename+" 完成")


def new_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
