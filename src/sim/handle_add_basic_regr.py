import os
from constants import VCM_REGR_FILENAME
from case.case_manager import CaseManager
from sim.sim_manager import SimManager
from item.regr_item import RegrItem
from item.sim_item import SimItem
from item.regr_list_item import RegrListItem
from utils.utils_case import get_cases_name_from_list
from utils.utils_log import Logger

def get_regr_log_name(status_log_path = "status.log", reg_info_log_path = "log/reg_info.log"):
  merged_data = []

  # 检查 status.log 文件是否存在
  if not os.path.exists(status_log_path):
    print(f"[VCM] Error: File '{status_log_path}' not found.")
    return []
  # 检查 reg_info.log 文件是否存在
  if not os.path.exists(reg_info_log_path):
    print(f"[VCM] Error: File '{reg_info_log_path}' not found.")
    return []

  # 读取 status.log 文件
  status_data = {}
  with open(status_log_path, 'r') as status_file:
    for line in status_file:
      parts = line.strip().split()
      if len(parts) == 3 and parts[0] == "job":
        _, job_id, case_name = parts
        status_data[job_id] = case_name

  # 读取 reg_info.log 文件并检查行数
  reg_info_data = []
  with open(reg_info_log_path, 'r') as reg_info_file:
    for line in reg_info_file:
      parts = line.strip().split()
      if len(parts) == 2:  # 只包含 case_name 和 case_seed
        case_name, case_seed = parts
        reg_info_data.append((case_name, case_seed))

  # 检查两个文件的行数
  if len(status_data) != len(reg_info_data):
    print(f"[VCM] Error: The number of lines in '{status_log_path}' and '{reg_info_log_path}' do not match.")
    print(f"[VCM] status.log lines: {len(status_data)}, reg_info.log lines: {len(reg_info_data)}")
    return []
 
  # 检查 case_name 是否一一对应
  case_names_status = set(status_data.values())
  case_names_reg_info = {case for case, _ in reg_info_data}

  if case_names_status != case_names_reg_info:
    print(f"[VCM] Error: Case names in '{status_log_path}' and '{reg_info_log_path}' do not match.")
    return []

  # 合并数据
  for case_name, case_seed in reg_info_data:
    if case_name in status_data.values():  # 检查 case 是否在 status_data 中
      job_id = next((jid for jid, cname in status_data.items() if cname == case_name), None)
      if job_id:
        merged_data.append((job_id, case_name, case_seed))

  return merged_data

def handle_add_basic_regr(cursor, loger:Logger, args):
  sim_manager = SimManager(cursor)
  case_manager = CaseManager(cursor)

  regr_items: list[RegrItem] = []

  # 检查当前目录
  current_dir = os.getcwd()
  if os.path.basename(current_dir) not in ("slurm", "regr"):
    print(f"[VCM] Error: Current directory '{current_dir}' is not 'slurm/regr'.")
    return
  
  # 检查是否有 VCM_REGR_FILENAME
  if not os.path.exists(VCM_REGR_FILENAME):
    print(f"[VCM] Error: File '{VCM_REGR_FILENAME}' not found.")
    return
  else:
    regr_list = RegrListItem.load_from_file()
    regr_items = regr_list.get_regrs()

  for regr_item in regr_items:
    regr_case_list = regr_item.case_list
    current_user = regr_item.current_user

    # clear old sim
    regr_item.clear_sims()

    # get case list
    caselist_names = get_cases_name_from_list(regr_case_list)

    case_names = get_regr_log_name()
    if not case_names:
      print(f"[VCM] Error: No case names found in log files.")
      return
    
    # 检查 case_names.case_name 是否与caselist_names一致
    for _, case_name, _ in case_names:
      if case_name not in caselist_names:
        print(f"[VCM] Error: Case name '{case_name}' not found in case list.")
        return

    for case_item in case_names:
      job_id, case_name, case_seed = case_item
      # 检查 case_name 是否存在
      if not case_manager.exist_case(case_name, regr_item.module_id):
        print(f"[VCM] Error: Case '{case_name}' not found in module '{regr_item.module_name}'.")
        return
      else:
        case_id = case_manager.find_case_id_by_module_id(case_name, regr_item.module_id)
        if not case_id:
          print(f"[VCM] Error: Case ID for '{case_name}' not found.")
          return
        
        #create sim 
        sim_id = sim_manager.add_sim_basic_regr(case_id, job_id, case_seed, current_user)

        if not sim_id:
          print(f"[VCM] Error: Failed to add simulation for case '{case_name}'.")
          return

        # 创建 SimItem 并加入 regr_item.sims
        sim_log_path = "None"
        sim_item = SimItem(sim_id, case_name, case_seed, job_id, sim_log_path)
        regr_item.add_sim(sim_item)
    print(f"[VCM] Successfully added basic regression for {len(regr_item.sims)} cases.")
    regr_list.update_regr(regr_item)

  # 保存 regr_item 到 JSON
  regr_list.save_to_file()
  