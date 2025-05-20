from item.task_item import TaskItem
from item.sim_item import SimItem
from item.base_item import BaseItem
from constants import get_current_user, get_current_dir, get_current_time, get_current_host, VCM_REGR_FILENAME
import json
import os

class RegrItem(BaseItem):
  def __init__(self, regr_id, regr_type, module_name, module_id=None):
    self.regr_id = regr_id
    self.regr_type = regr_type
    self.module_name = module_name
    self.module_id = module_id
    self.current_dir = get_current_dir()
    self.current_time = get_current_time()
    self.current_user = get_current_user()
    self.current_host = get_current_host()
    self.tasks = []
    self.part_name = None
    self.part_mode = None
    self.node_name = None
    self.work_name = None
    self.work_url = None
    self.case_list = None
    self.sims = []

  def to_dict(self):
    return {
      "regr_id": self.regr_id,
      "regr_type": self.regr_type,
      "module_name": self.module_name,
      "module_id": self.module_id,
      "current_dir": self.current_dir,
      "current_time": self.current_time,
      "current_user": self.current_user,
      "current_host": self.current_host,
      "part_name": self.part_name,
      "part_mode": self.part_mode,
      "node_name": self.node_name,
      "work_name": self.work_name,
      "work_url": self.work_url,
      "case_list": self.case_list,
      "tasks": [task.to_dict() for task in self.tasks] if self.tasks else [],
      "sims": [sim.to_dict() for sim in self.sims] if self.sims else [],
    }

  @classmethod
  def from_dict(cls, data):
    item = cls(
      data.get("regr_id"),
      data.get("regr_type"),
      data.get("module_name"),
      data.get("module_id"),
    )
    item.current_dir = data.get("current_dir")
    item.current_time = data.get("current_time")
    item.current_user = data.get("current_user")
    item.current_host = data.get("current_host")
    
    item.part_name = data.get("part_name")
    item.part_mode = data.get("part_mode")
    item.node_name = data.get("node_name")
    item.work_name = data.get("work_name")
    item.work_url = data.get("work_url")
    item.case_list = data.get("case_list")

    item.tasks = [TaskItem.from_dict(t) for t in data.get("tasks", [])]
    item.sims = [SimItem.from_dict(s) for s in data.get("sims", [])]
    return item

  def save_to_file(self, path=VCM_REGR_FILENAME):
    with open(path, "w") as f:
      json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

  @classmethod
  def load_from_file(cls, path=VCM_REGR_FILENAME):
    if not os.path.exists(path):
      return None
    if os.path.getsize(path) == 0:  # 文件为空
      return None
    with open(path, "r") as f:
      data = json.load(f)
    return cls.from_dict(data)
  
  def get_sims(self):
    """返回所有 sim 的列表"""
    return self.sims
  
  def get_sims_dict(self):
    """返回所有 sim 的 dict 列表"""
    return [sim.to_dict() for sim in self.sims]

  def set_sims(self, sim_list):
    self.sims = []
    for sim in sim_list:
      if isinstance(sim, SimItem):
        self.sims.append(sim)
      else:
        sim_item = SimItem.from_dict(sim)
        self.sims.append(sim_item)
  
  def add_sim(self, sim):
    """添加单个 sim，支持 SimItem 或 dict"""
    if not isinstance(sim, SimItem):
      sim = SimItem.from_dict(sim)
    # 避免重复（可按 sim_id 或 case_name, case_seed, sim_log 唯一性）
    key = (sim.case_name, sim.case_seed, sim.sim_log)
    for s in self.sims:
      if (s.case_name, s.case_seed, s.sim_log) == key:
        return
    self.sims.append(sim)

  def remove_sim(self, sim_id):
    """根据 sim_id 移除 sim"""
    self.sims = [s for s in self.sims if s.sim_id != sim_id]

  def clear_sims(self):
    self.sims = []
  
  def get_tasks(self):
    return self.tasks
  
  def get_tasks_dict(self):
    """返回所有 task 的 dict 列表"""
    return [task.to_dict() for task in self.tasks]
  
  def set_tasks(self, task_list):
    self.tasks = []
    for task in task_list:
      if isinstance(task, TaskItem):
        self.tasks.append(task)
      else:
        task_item = TaskItem.from_dict(task)
        self.tasks.append(task_item)

  def clear_tasks(self):
    self.tasks = []

  def add_task(self, task):
    """添加单个 task，支持 TaskItem 或 dict"""
    if not isinstance(task, TaskItem):
      task = TaskItem.from_dict(task)
    # 避免重复（可按 task_id 唯一性）
    for t in self.tasks:
      if t.task_id == task.task_id:
        return
    self.tasks.append(task)

  def remove_task(self, task_id):
    """根据 task_id 移除 task"""
    self.tasks = [t for t in self.tasks if t.task_id != task_id]