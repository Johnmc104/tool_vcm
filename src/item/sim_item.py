import json
import os
from constants import get_current_time, get_current_user

class SimItem:
  def __init__(self, 
    sim_id, case_name, case_seed, job_id, status="None", sim_log="None", check_result=None,created_time=None, current_user=None
    
  ):
    self.sim_id = sim_id
    self.case_name = case_name
    self.case_seed = case_seed
    self.job_id = job_id
    self.status = status
    self.sim_log = sim_log
    self.check_result = check_result
    self.created_time = created_time if created_time is not None else get_current_time()
    
  def to_dict(self):
    return {
      "sim_id": self.sim_id,
      "case_name": self.case_name,
      "case_seed": self.case_seed,
      "job_id": self.job_id,
      "status": self.status,
      "sim_log": self.sim_log,
      "check_result": self.check_result,
      "created_time": self.created_time
    }


  @staticmethod
  def from_dict(data):
    return SimItem(
      sim_id=data.get("sim_id"),
      case_name=data.get("case_name"),
      case_seed=data.get("case_seed"),
      job_id=data.get("job_id"),
      status=data.get("status", "None"),
      sim_log=data.get("sim_log", "None"),
      check_result=data.get("check_result"),
      created_time=data.get("created_time")
    )

  @staticmethod
  def load_sim_logs(file_path):
    if not os.path.exists(file_path):
      return []
    with open(file_path, "r") as f:
      data = json.load(f)
    return [SimItem.from_dict(item) for item in data.get("sim_logs", [])]

  @staticmethod
  def save_sim_logs(file_path, sim_logs):
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