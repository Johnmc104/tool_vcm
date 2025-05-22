import os
import json
from constants import NODE_MAP
from item.regr_item import RegrItem
from item.sim_item import SimItem
from item.task_item import TaskItem
from item.regr_list_item import RegrListItem
from utils.utils_env import get_job_status_name
from sim.sim_manager import SimManager
from typing import List

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

def update_sim_info(
  sim_info: SimItem,
  regr_item: RegrItem,
  sim_manager: SimManager,
  task_items: List[TaskItem]
):
  sim_id = sim_info.sim_id
  job_id = sim_info.job_id
  if not job_id:
    print(f"[VCM] Warning: sim_id '{sim_id}' has no job_id, skipping.")
    return sim_info, task_items, False

  status, node_name, job_status = get_job_status_name(job_id)
  if status is None or node_name is None:
    print(f"[VCM] Warning: job_id '{job_id}' status not found, skipping.")
    return sim_info, task_items, False
  sim_info.job_status = job_status

  case_name = getattr(sim_info, "case_name", None)
  if not case_name:
    print(f"[VCM] Warning: sim_id '{sim_id}' has no case_name, skipping.")
    return sim_info, task_items, False

  if status == "OK":
    case_seed = sim_info.case_seed
    sim_log_path = get_regr_sim_log_path(
      node_name, regr_item.current_user, regr_item.work_name, case_name, case_seed
    )
    if os.path.exists(sim_log_path):
      sim_info.sim_log = sim_log_path
      sim_info.status = "TODO"
      print(f"[VCM] sim_id '{sim_id}' (job_id '{job_id}'): Updated simulation log path to '{sim_log_path}'.")
      task_items, assigned = assign_sim_to_task(sim_info, node_name, task_items, sim_manager, regr_item)
      if not assigned:
        print(f"[VCM] Warning: No task found for node '{node_name}', sim_id '{sim_id}' not assigned.")
      return sim_info, task_items, assigned
    else:
      print(f"[VCM] sim_id '{sim_id}' (job_id '{job_id}'): Simulation log file '{sim_log_path}' not found.")
      return sim_info, task_items, False
  else:
    print(f"[VCM] sim_id '{sim_id}' (job_id '{job_id}'): job_status is '{job_status}', not update.")
    return sim_info, task_items, False

def assign_sim_to_task(
  sim_info: SimItem,
  node_name: str,
  task_items: List[TaskItem],
  sim_manager: SimManager,
  regr_item: RegrItem
):
  sim_id = sim_info.sim_id
  job_id = sim_info.job_id
  found_task = False
  new_task_items = []

  for task in task_items:
    task_node = task.current_host
    if task_node and task_node == node_name:
      if not hasattr(task, "sim_logs") or task.sim_logs is None:
        task.sim_logs = []
      already_in = any(
        getattr(log, "sim_id", None) == sim_id or getattr(log, "job_id", None) == job_id
        for log in task.sim_logs
      )
      if not already_in:
        task.add_sim(sim_info)
        sim_manager.update_sim_task_id(sim_id, task.task_id)
        print(f"[VCM] sim_id '{sim_id}' assigned to task on node '{node_name}'.")
      found_task = True
      regr_item.update_task(task)
    new_task_items.append(task)

  return new_task_items, found_task

def process_regr_item(
  regr_item: RegrItem,
  sim_manager: SimManager
) -> RegrItem:
  sim_items = regr_item.get_sims()
  if not sim_items:
    print("[VCM] Error: No simulation data found in regr_item.")
    return regr_item

  task_items = regr_item.get_tasks()
  if not task_items:
    print("[VCM] Error: No tasks found in regr_item.")
    return regr_item

  new_sim_items = []
  for sim_info in sim_items:
    sim_info, task_items, updated = update_sim_info(sim_info, regr_item, sim_manager, task_items)
    if not updated:
      new_sim_items.append(sim_info)
    regr_item.set_tasks(task_items)
    
  regr_item.set_sims(new_sim_items)
  return regr_item

def handle_update_node_dir(cursor, args):
  regr_list:RegrListItem
  sim_manager = SimManager(cursor)

  if os.path.basename(os.getcwd()) != "slurm":
    print("[VCM] Error: Current directory must be 'slurm'.")
    return
  
  regr_list = RegrListItem.load_from_file()
  regr_items = regr_list.get_regrs()
  if not regr_items:
    print("[VCM] Error: No regression items found.")
    return
  
  new_regr_items = []
  for regr_item in regr_items:
    updated_regr = process_regr_item(regr_item, sim_manager)
    new_regr_items.append(updated_regr)
  regr_list.set_regrs(new_regr_items)
  regr_list.save_to_file()
  print("[VCM] Simulation info updated and saved to regr_item.")