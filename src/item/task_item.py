from typing import List, Optional
from item.sim_item import SimItem
from constants import get_current_user, get_current_dir, get_current_time, get_current_host, VCM_TASK_FILENAME
import json
import os

class TaskItem:
  def __init__(
        self,
        task_id=None,
        status_init="None",
        status_post="None",
        status_regr="None",
        status_check="None",
        git_de="None",
        git_dv="None",
        comp_log_time=None,
        current_user=None,
        current_host=None,
        sim_logs=None
    ):
        self.task_id = task_id
        self.status_init = status_init
        self.status_post = status_post
        self.status_regr = status_regr
        self.status_check = status_check
        self.git_de = git_de
        self.git_dv = git_dv
        self.comp_log_time = comp_log_time
        self.current_user = current_user if current_user is not None else get_current_user()
        self.current_host = current_host if current_host is not None else get_current_host()
        self.sim_logs = sim_logs if sim_logs is not None else []

  @classmethod
  def load_from_file(cls, file_path = VCM_TASK_FILENAME):
    """
    文件不存在时，返回默认 TaskItem
    """
    if os.path.exists(file_path):
      with open(file_path, "r") as f:
        data = json.load(f)
      return cls.from_dict(data)
    return cls()

  def save_to_file(self, file_path = VCM_TASK_FILENAME):
    with open(file_path, "w") as f:
      json.dump(self.to_dict(), f, indent=2)

  def to_dict(self):
    return {
      "task_id": self.task_id,
      "status_init": self.status_init,
      "status_post": self.status_post,
      "status_regr": self.status_regr,
      "status_check": self.status_check,
      "Git_DE": self.git_de,
      "Git_DV": self.git_dv,
      "comp_log_time": self.comp_log_time,
      "current_user": self.current_user,
      "current_host": self.current_host,
      "sim_logs": self.sim_logs
    }
  
  @staticmethod
  def from_dict(data: dict):
    return TaskItem(
      task_id=data.get("task_id"),
      status_init=data.get("status_init", "None"),
      status_post=data.get("status_post", "None"),
      status_regr=data.get("status_regr", "None"),
      status_check=data.get("status_check", "None"),
      git_de=data.get("Git_DE", "None"),
      git_dv=data.get("Git_DV", "None"),
      comp_log_time=data.get("comp_log_time"),
      current_user=data.get("current_user", get_current_user()),
      current_host=data.get("current_host", get_current_host()),
      sim_logs=data.get("sim_logs", [])
    )

  def update_sim_logs(self, new_logs: list):
    # 合并去重
    #print(f"[VCM] Merging new sim logs into existing logs.")
    # 读取现有的 sim_logs
    #print(f"[VCM] Existing sim logs: {self.sim_logs}")
    existing = { (log.get("case_name"), log.get("case_seed"), log.get("sim_log")) for log in self.sim_logs }
    for log in new_logs:
      #print(f"[VCM] Processing new log: {log}")
      key = (log.get("case_name"), log.get("case_seed"), log.get("sim_log"))
      if key not in existing:
        self.sim_logs.append(log)
        existing.add(key)
      else:
        print(f"[VCM] Duplicate log found, skipping: {log}")
        pass
    #print(f"[VCM] Updated sim logs: {self.sim_logs}")

  def get_post_status(self):
    if self.status_post == "False" or self.status_post == "None":
      return False
    else:
      return True