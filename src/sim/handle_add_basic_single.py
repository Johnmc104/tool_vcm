import os
import json
from sim.sim_manager import SimManager
from module.module_manager import ModuleManager
from case.case_manager import CaseManager
from constants import *
from utils.utils_git import get_module_name
from utils.utils_case import find_case_sw_info, find_case_hw_info
from constants import get_current_user, get_current_dir
from item.sim_item import SimItem
from item.task_item import TaskItem
from sim.handle_sim_time_pass import process_single_sim_info

def handle_add_basic_single(cursor, logger, args):
  module_manager = ModuleManager(cursor)
  case_manager = CaseManager(cursor)
  sim_manager = SimManager(cursor)

  current_user = get_current_user()
  current_dir = get_current_dir()

  # get taskitem
  task_dicts = TaskItem.load_from_file(VCM_TASK_FILENAME)

  if not task_dicts:
    print("[VCM] Error: No task info found.")
    return
  
  # check sim_log file is valid
  sim_log_path = os.path.join(current_dir, args.sim_log_path)
  if not os.path.exists(sim_log_path):
    print(f"[VCM] Error: Sim log file '{sim_log_path}' not found.")
    return

  # get case_name and case_seed from sim.log
  case_name, case_seed = find_case_hw_info(sim_log_path)
  if not case_name or not case_seed:
    print("[VCM] Error: Case name/seed not found in sim.log.")
    return

  # check module_name
  module_name = get_module_name(args)
  if not module_name:
    print("[VCM] Error: Module name not found in sim.log.")
    return
  else:
    module_id = module_manager.find_module_id_by_name(module_name)

  # check case is exist
  case_id = case_manager.find_case_id_by_module_id(case_name, module_id)
  if not case_id:
    print(f"[VCM] Error: Case '{case_name}' does not exist under module '{module_name}'.")
    case_manager.add_case_basic(case_name, module_id, current_user)
    case_id = case_manager.find_case_id_by_module_id(case_name, module_id)
    group_name, case_c_name = find_case_sw_info(case_name)
    if not group_name or not case_c_name:
      print(f"[VCM] Error: Case '{case_name}' not found in case_info.")
      return
    else:
      case_manager.update_case_st(case_id, group_name, case_c_name)
    print(f"[VCM] Case '{case_name}' added under module '{module_name}'.")

  # 读取/初始化 vcm_task_info.json 的 sim_logs
  sim_logs = SimItem.load_sim_logs(VCM_TASK_FILENAME)


  # 检查是否已存在该 sim.log 记录，防止重复写入
  if SimItem.exists(sim_logs, case_name, case_seed, sim_log_path):
    exist_log = SimItem.exists(sim_logs, case_name, case_seed, sim_log_path)
    print(f"[VCM] Sim log for case '{case_name}' with seed '{case_seed}' already exists (sim_id: {exist_log.sim_id}). Skipping.")
    return

  # 读取 task_id
  if os.path.exists(VCM_TASK_FILENAME):
    with open(VCM_TASK_FILENAME, "r") as f:
      task_info = json.load(f)
    task_id = task_info.get("task_id")
  else:
    print("[VCM] Error: Task info file not found.")
    return
  
  # 写入 sim_info
  sim_id = sim_manager.add_sim_basic_single(case_id, case_seed, task_id, current_user)
  print(f"[VCM] Basic single simulation added with ID '{sim_id}', case name '{case_name}', seed '{case_seed}'.")

  # 构造 SimItem 并追加
  sim_item = SimItem(sim_id, case_name, case_seed, 0, "TODO", sim_log_path)
  #print(f"[VCM] SimItem created with ID '{sim_item.sim_id}', case name '{sim_item.case_name}', seed '{sim_item.case_seed}', sim_log '{sim_item.sim_log}'.")
  
  post_flag = task_dicts.get_post_status()

  sim_info = sim_item.to_dict()
  sim_info = process_single_sim_info(args, sim_manager, sim_info, post_flag)
  print(f"[VCM] Processed sim info: {sim_info}")

  sim_logs.append(sim_info)

  sim_dics = []
  for sim in sim_logs:
    #check sim is sim_item or dict
    if isinstance(sim, SimItem):
      sim_dic = sim
    else:
      sim_dic = SimItem.from_dict(sim)
    sim_dics.append(sim_dic.to_dict())

  print(f"[VCM] Sim logs updated with new entry: {sim_dics}")
  
  # 更新 task_dicts 中的 sim_logs
  task_dicts.update_sim_logs(sim_dics)
  task_dicts.save_to_file(VCM_TASK_FILENAME)