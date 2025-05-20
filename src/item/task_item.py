from typing import List, Optional
from item.sim_item import SimItem
from item.base_item import BaseItem
from constants import get_current_user, get_current_dir, get_current_time, get_current_host, VCM_TASK_FILENAME
import json
import os

class TaskItem(BaseItem):
  def __init__(
    self,
    task_id=None,
    status_post="None",
    status_regr="None",
    status_check="None",
    git_de="None",
    git_dv="None",
    comp_log_time=None,
    current_user=None,
    current_host=None,
    sim_logs: List[SimItem]=None
  ):
    self.task_id = task_id
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
      "status_post": self.status_post,
      "status_regr": self.status_regr,
      "status_check": self.status_check,
      "git_de": self.git_de,
      "git_dv": self.git_dv,
      "comp_log_time": self.comp_log_time,
      "current_user": self.current_user,
      "current_host": self.current_host,
      "sim_logs": [log.to_dict() for log in self.sim_logs]
    }
  
  @staticmethod
  def from_dict(data: dict):
    return TaskItem(
      task_id=data.get("task_id"),
      status_post=data.get("status_post", "None"),
      status_regr=data.get("status_regr", "None"),
      status_check=data.get("status_check", "None"),
      git_de=data.get("git_de", "None"),
      git_dv=data.get("git_dv", "None"),
      comp_log_time=data.get("comp_log_time"),
      current_user=data.get("current_user", get_current_user()),
      current_host=data.get("current_host", get_current_host()),
      sim_logs=[SimItem.from_dict(item) for item in data.get("sim_logs", [])]
    )

  def update_sim_logs(self, new_logs: list):
    # 合并去重
    #print(f"[VCM] Merging new sim logs into existing logs.")
    # 读取现有的 sim_logs
    #print(f"[VCM] Existing sim logs: {self.sim_logs}")
    existing = { (log.case_name, log.case_seed, log.sim_log) for log in self.sim_logs }
    for log in new_logs:
      #print(f"[VCM] Processing new log: {log}")
      key = (log.case_name, log.case_seed, log.sim_log)
      if key not in existing:
        self.sim_logs.append(log)
        existing.add(key)
      else:
        print(f"[VCM] Duplicate log found, skipping: {log.to_dict()}")
        pass
    #print(f"[VCM] Updated sim logs: {self.sim_logs}")

  def get_post_status(self):
    if self.status_post == "False" or self.status_post == "None":
      return False
    else:
      return True
    
  def clear_sim_logs(self):
    self.sim_logs = []

  def get_sims(self):
    """获取所有 sim_logs 列表"""
    return self.sim_logs

  def get_sim_logs(self):
    """获取所有 sim_logs 列表"""
    return self.sim_logs

  def set_sim_logs(self, sim_logs):
    """批量设置 sim_logs，支持 SimItem 或 dict"""
    self.sim_logs = []
    for sim in sim_logs:
      if isinstance(sim, SimItem):
        self.sim_logs.append(sim)
      else:
        self.sim_logs.append(SimItem.from_dict(sim))

  def add_sim(self, sim):
    """添加单个 sim_log，支持 SimItem 或 dict"""
    if not isinstance(sim, SimItem):
      sim = SimItem.from_dict(sim)
    # 避免重复
    key = (sim.case_name, sim.case_seed, sim.sim_log)
    for log in self.sim_logs:
      if (log.case_name, log.case_seed, log.sim_log) == key:
        return  # 已存在则不添加
    self.sim_logs.append(sim)

  def remove_sim(self, sim_id):
    """根据 sim_id 移除 sim_log"""
    self.sim_logs = [s for s in self.sim_logs if s.sim_id != sim_id]