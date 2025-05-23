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
from utils.utils_log import Logger

def handle_add_basic_single(cursor, logger:Logger, args):
  module_manager = ModuleManager(cursor)
  case_manager = CaseManager(cursor)
  sim_manager = SimManager(cursor)

  current_user = get_current_user()
  current_dir = get_current_dir()

  # get taskitem
  task_item = TaskItem.load_from_file(VCM_TASK_FILENAME)
  if not task_item:
    logger.log("No task info found.", level="ERROR")
    return
  
  task_id = task_item.task_id
  
  # check sim_log file is valid
  sim_log_path = os.path.join(current_dir, args.sim_log_path)
  if not os.path.exists(sim_log_path):
    logger.log(f"Sim log file '{sim_log_path}' not found.", level="ERROR")
    return

  # get case_name and case_seed from sim.log
  case_name, case_seed = find_case_hw_info(sim_log_path)
  if not case_name or not case_seed:
    logger.log(f"Case name/seed not found in sim.log: {sim_log_path}", level="ERROR")
    return

  # check module_name
  module_name = get_module_name(args)
  if not module_name:
    logger.log(f"Module name not found in sim.log: {sim_log_path}", level="ERROR")
    return
  else:
    module_id = module_manager.find_module_id_by_name(module_name)

  # check case is exist
  case_id = case_manager.find_case_id_by_module_id(case_name, module_id)
  if not case_id:
    logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="ERROR")
    case_manager.add_case_basic(case_name, module_id, current_user)
    case_id = case_manager.find_case_id_by_module_id(case_name, module_id)
    group_name, case_c_name = find_case_sw_info(case_name)
    if not group_name or not case_c_name:
      logger.log(f"Case '{case_name}' not found in case_info.", level="ERROR")
      return
    else:
      case_manager.update_case_st(case_id, case_c_name, group_name)
    logger.log(f"Case '{case_name}' added under module '{module_name}'.", level="INFO")

  # 读取/初始化 vcm_task_info.json 的 sim_logs
  sim_logs = SimItem.load_from_file(VCM_TASK_FILENAME)

  # 检查是否已存在该 sim.log 记录，防止重复写入
  exist_log = SimItem.exists(sim_logs, case_name, case_seed, sim_log_path)
  if exist_log:
    logger.log(f"Sim log for case '{case_name}' with seed '{case_seed}' already exists (sim_id: {exist_log.sim_id}). Skipping.", level="INFO")
    return
 
  # 写入 sim_info
  sim_id = sim_manager.add_sim_basic_single(case_id, case_seed, task_id, current_user)
  logger.log(f"Basic single simulation added with ID '{sim_id}', case name '{case_name}', seed '{case_seed}'.", level="INFO")

  # 构造 SimItem 并追加
  sim_item = SimItem(sim_id, case_name, case_seed, 0, "TODO", sim_log_path)
  #print(f"[VCM] SimItem created with ID '{sim_item.sim_id}', case name '{sim_item.case_name}', seed '{sim_item.case_seed}', sim_log '{sim_item.sim_log}'.")
  
  post_flag = task_item.get_post_status()

  sim_info = sim_item.to_dict()
  sim_info = process_single_sim_info(logger, args, sim_manager, sim_info, post_flag)
  #print(f"[VCM] Processed sim info: {sim_info}")

  sim_logs.append(SimItem.from_dict(sim_info))

  # 更新 task_item 中的 sim_logs
  task_item.update_sim_logs(sim_logs)
  task_item.save_to_file(VCM_TASK_FILENAME)