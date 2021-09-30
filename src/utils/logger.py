import logging
import sys

# import colorlog


def init_logging():
    """
    Initialize logger.

    Returns
    -------
        logger object
    """
    logger = logging.getLogger("SPARK")
    logger.setLevel(logging.DEBUG)
    # fh = logging.FileHandler('my_log_info.log')
    sh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s] %(message)s",
        datefmt="%a, %d %b %Y %H:%M:%S",
    )
    sh.setFormatter(formatter)
    # fh.setFormatter(formatter)
    # sh.setFormatter(
    #     colorlog.ColoredFormatter(
    #         "%(log_color)s [%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
    #         datefmt="%a, %d %b %Y %H:%M:%S",
    #     )
    # )
    # logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
