import os
import json
from constants import NODE_MAP, FILE_VCM_TASK
from sim.sim_manager import SimManager
from item.regr_item import RegrItem
from item.sim_item import SimItem
from item.task_item import TaskItem

def get_regr_node_name(status_log_path="status_check.log"):
  jobid_sim_map = {}

  if not os.path.exists(status_log_path):
    print(f"[VCM] Error: Log file '{status_log_path}' not found.")
    return

  with open(status_log_path, 'r') as file:
    for line in file:
      parts = line.split()
      if len(parts) < 5:
        print("[VCM] Error: Incomplete line in status log, skipping.")
        continue

      job_id = parts[1]
      if "PENDING" in line:
        node_name = "pending"
        case_name = parts[4]
        status = "PENDING"
      elif "FAILED" in line or "CANCELLED" in line or "TIMEOUT" in line:
        node_name = "default_node"
        case_name = parts[4]
        status = "FAILED"
      elif "COMPLETED" in line:
        node_name = parts[3]
        case_name = parts[4]
        status = "OK"
      elif "CONFIGURING" in line or "COMPLETING" in line or "RUNNING" in line or "PREEMPTED" in line:
        node_name = parts[3]
        case_name = parts[4]
        status = "RUNNING"
      else:
        continue
      jobid_sim_map[job_id] = {
        "node_name": node_name,
        "case_name": case_name,
        "status": status
      }
  return jobid_sim_map

def get_regr_sim_log_path(node_name, user_name, work_name, case_name, case_seed):
  node_dir = "/" + NODE_MAP.get(node_name)
  case_name_seed = case_name + "_" + case_seed
  sim_log_name = case_name_seed + ".log"
  file_path = os.path.join(
    node_dir, "work", user_name , work_name, "regr", case_name, case_name_seed, sim_log_name
    )
  return file_path


def handle_update_node_dir(cursor, args):
  sim_manager = SimManager(cursor)

  if os.path.basename(os.getcwd()) != "slurm":
    print("[VCM] Error: Current directory must be 'slurm'.")
    return

  regr_item = RegrItem.load_from_json()
  sim_dicts = regr_item.get_sims()
  if not sim_dicts:
    print("[VCM] Error: No simulation data found in regr_item.")
    return

  node_sim_map = get_regr_node_name()
  if not node_sim_map:
    print("[VCM] Error: Unable to parse node name or simulation directory from log.")
    return

  tasks = getattr(regr_item, "tasks", [])
  if not tasks:
    print("[VCM] Error: No tasks found in regr_item.")
    return

  sims_to_remove = []
  for sim_info in sim_dicts:
    sim_id = sim_info.get("sim_id")
    job_id = sim_info.get("job_id")
    if not job_id:
      print(f"[VCM] Warning: sim_id '{sim_id}' has no job_id, skipping.")
      continue

    node_info = node_sim_map.get(job_id)
    if not node_info:
      print(f"[VCM] Warning: job_id '{job_id}' not found in node_sim_map, skipping.")
      continue

    status = node_info["status"]
    node_name = node_info["node_name"]
    case_name = node_info["case_name"]

    if status == "OK":
      case_seed = sim_info.get("case_seed")
      sim_log_path = get_regr_sim_log_path(
        node_name, regr_item.current_user, regr_item.work_name, case_name, case_seed
      )
      if os.path.exists(sim_log_path):
        sim_info["sim_log"] = sim_log_path
        sim_info["status"] = "TODO"
        print(f"[VCM] sim_id '{sim_id}' (job_id '{job_id}'): Updated simulation log path to '{sim_log_path}'.")

        # 只分配到node匹配的task，且避免重复
        found_task = False
        for task in tasks:
          task_node = getattr(task, "current_host", None)
          if task_node and task_node == node_name:
            if not hasattr(task, "sim_logs") or task.sim_logs is None:
              task.sim_logs = []
            # 避免重复添加
            already_in = any(
              getattr(log, "sim_id", None) == sim_id or getattr(log, "job_id", None) == job_id
              for log in task.sim_logs
            )
            if not already_in:
              task.sim_logs.append(SimItem.from_dict(sim_info))
              print(f"[VCM] sim_id '{sim_id}' assigned to task on node '{node_name}'.")
            found_task = True
            break

        if not found_task:
          print(f"[VCM] Warning: No task found for node '{node_name}', sim_id '{sim_id}' not assigned.")
        else:
          sims_to_remove.append(sim_info)
      else:
        print(f"[VCM] sim_id '{sim_id}' (job_id '{job_id}'): Simulation log file '{sim_log_path}' not found.")
    else:
      print(f"[VCM] sim_id '{sim_id}' (job_id '{job_id}'): Status is '{status}', not update.")

  # 从 sims 中移除已归档的 sim
  for sim in sims_to_remove:
    if sim in sim_dicts:
      sim_dicts.remove(sim)

  # 写回 regr_item 并保存
  regr_item.set_sims(sim_dicts)
  regr_item.tasks = tasks
  regr_item.save_to_json()
  print("[VCM] Simulation info updated and saved to regr_item.")