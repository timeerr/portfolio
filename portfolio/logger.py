import logging


def get_logger():
    return logging.getLogger('portfolio')


def info(mssg):
    get_logger().info(mssg)


def warning(mssg):
    get_logger().warning(mssg)
