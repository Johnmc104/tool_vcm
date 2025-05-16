from loguru import logger
import inspect
import sys
import datetime

class Logger:
  def __init__(self, level="INFO"):
    # 配置 loguru logger
    logger.remove()  # 移除默认的日志处理器
    logger.add(sys.stderr, level=level)  # 设置全局日志级别
    logger.configure(handlers=[
      {
        "sink": sys.stderr,
        "format": "[VCM] <level>{level: <8}{message}</level>",
        "colorize": True
      },
    ])

  def log(self, msg, level="INFO"):
    # 获取调用堆栈信息
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    fileline = frame.f_lineno
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"{filename}({fileline}) @ {time} : {msg}"
    #formatted_msg = f"[{level}] {filename}({fileline}) @ {time} : {msg}"
    #formatted_msg = f"{msg}"

    if level == "DEBUG":
      logger.debug(formatted_msg)
    elif level == "WARNING":
      logger.warning(formatted_msg)
    elif level == "ERROR":
      logger.error(formatted_msg)
    else:
      logger.info(formatted_msg)
