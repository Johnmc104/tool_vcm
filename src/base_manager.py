from constants import REMOTE_EN, REMOTE_API_URL


class BaseManager:
  ENDPOINT_PROJECT = "/projects"

  def __init__(self, cursor):
    self.use_remote = REMOTE_EN
    self.remote_url = REMOTE_API_URL
    if not self.use_remote:
      self.cursor = cursor

class CommonManager(BaseManager):
  def common_method(self):
    # 通用业务逻辑
    pass