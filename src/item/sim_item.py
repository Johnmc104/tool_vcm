from item.base_item import BaseItem
import json
import os
from constants import get_current_time

class SimItem(BaseItem):
  def __init__(self, 
    sim_id, case_name, case_seed, 
    job_id, job_status="None",
    status="None", sim_log="None", sim_result=None, created_time=None
  ):
    self.sim_id = sim_id
    self.case_name = case_name
    self.case_seed = case_seed
    self.job_id = job_id
    self.job_status = job_status
    self.status = status
    self.sim_log = sim_log
    self.sim_result = sim_result
    self.created_time = created_time if created_time is not None else get_current_time()

  def to_dict(self):
    return {
      "sim_id": self.sim_id,
      "case_name": self.case_name,
      "case_seed": self.case_seed,
      "job_id": self.job_id,
      "job_status": self.job_status,
      "status": self.status,
      "sim_log": self.sim_log,
      "sim_result": self.sim_result,
      "created_time": self.created_time
    }

  @classmethod
  def from_dict(cls, data):
    return cls(
      sim_id=data.get("sim_id"),
      case_name=data.get("case_name"),
      case_seed=data.get("case_seed"),
      job_id=data.get("job_id"),
      job_status=data.get("job_status", "None"),
      status=data.get("status", "None"),
      sim_log=data.get("sim_log", "None"),
      sim_result=data.get("sim_result"),
      created_time=data.get("created_time")
    )

  @classmethod
  def load_from_file(cls, file_path):
    if not os.path.exists(file_path):
      return []
    with open(file_path, "r") as f:
      data = json.load(f)
    return [cls.from_dict(item) for item in data.get("sim_logs", [])]

  @classmethod
  def save_to_file(cls, file_path, sim_logs):
    with open(file_path, "w") as f:
      json.dump({"sim_logs": [log.to_dict() for log in sim_logs]}, f, indent=2)

  @staticmethod
  def exists(sim_logs, case_name, case_seed, sim_log):
    for log in sim_logs:
      if (log.case_name == case_name and
          log.case_seed == case_seed and
          log.sim_log == sim_log):
        return log
    return None
