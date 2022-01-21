''' init '''
import logging
import os
import sys

# 解决windows环境python3.8下可能出现的问题
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from tornado.options import define, options, parse_config_file

if not options.__contains__("config_load_flag"):
    # 将父目录添加到环境
    WORKSPACE_PATH = os.getcwd()
    BASE_PATH = os.path.dirname(WORKSPACE_PATH)
    sys.path.insert(0, BASE_PATH)
    logging.info("Server start at: %s", BASE_PATH)

    # 配置文件路径
    CONFIG_PATH = os.path.abspath(os.path.join(WORKSPACE_PATH, "./conf"))
    CONFIG_FILE = os.path.join(CONFIG_PATH, "tornado.conf")

    # 模型路径
    MODEL_PATH = os.path.join(WORKSPACE_PATH, "./models")
    SITE_PACKAGES_PATH = os.path.join(WORKSPACE_PATH, "runtime", "python", "site-packages")

    # 加载配置文件
    print("Init server...")
    define("config_load_flag", default=0, type=int, help="config load flag")
    define("http_port", default=13310, type=int, help="server port")
    define("config_path", default=CONFIG_PATH, type=str, help="config path")
    define("model_path", default=MODEL_PATH, type=str, help="model path")
    define("db_type", default="mysql", type=str, help="db type")
    define("site_packages_path", default=SITE_PACKAGES_PATH, type=str, help="site packages path")
    define("static_path", default="./static", type=str, help="static path")
    define("settings", default={}, type=dict, help="application settings")
    parse_config_file(CONFIG_FILE)

    options.config_path = CONFIG_PATH
    options.model_path = os.path.abspath(options.model_path)
    options.site_packages_path = os.path.abspath(options.site_packages_path)
    options.static_path = os.path.abspath(options.static_path)
    options.settings = {
        "static_path": options.static_path,
        "static_url_prefix": "/static/",
    }
    sys.path.insert(0, options.site_packages_path)


def get_options():
    return options
