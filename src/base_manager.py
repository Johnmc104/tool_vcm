"""
所有Manager的基类，统一数据库连接
"""
class BaseManager:
  def __init__(self, cursor):
    self.cursor = cursor

class CommonManager(BaseManager):
  def common_method(self):
    # 通用业务逻辑
    pass