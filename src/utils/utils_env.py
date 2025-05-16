import os
import re
import random
from glob import glob
from constants import NODE_MAP, get_current_user,get_current_dir, VCM_TASK_FILENAME
from constants import check_vtool_home

def determine_regr_type(logger):
  """
  根据当前目录名判断回归类型。
  ...
  """
  current_dir_name = os.path.basename(get_current_dir())
  if current_dir_name.startswith("sim_pre") or current_dir_name.startswith("sim_post") or current_dir_name.startswith("sim"):
    return None
  if current_dir_name.startswith("regr"):
    return "eman"
  if current_dir_name.startswith("slurm"):
    return "slurm"
  logger.log(f"[VCM] Unknown regr type '{current_dir_name}'. ", level="WARNING")
  return None
    
def check_comp_result(logger, log_file_path):
  # 定义正则表达式模式
  elaboration_pattern = r'Verdi KDB elaboration done'

  # 读取日志文件
  with open(log_file_path, 'r') as file:
    lines = file.readlines()

  # 检查是否有足够的行
  if len(lines) < 2:
    logger.log(f"Log file '{log_file_path}' does not have enough lines.", level="ERROR")
    return False

  # 获取最后两行
  last_two_lines = [line.strip() for line in lines[-2:]]

  # 检查最后是否符合模式
  if re.search(elaboration_pattern, last_two_lines[1]) :
    logger.log(f"Found expected pattern in log file '{log_file_path}'.", level="INFO")
    return True
  else:
    logger.log(f"Log file '{log_file_path}' does not contain the expected pattern.", level="ERROR")
    return False

def get_comp_corner(logger, comp_log_path="comp.log"):
  if not os.path.exists(comp_log_path):
    logger.error(f"[VCM] Error: Log file '{comp_log_path}' does not exist.")
    return None

  with open(comp_log_path, 'r') as file:
    for i, line in enumerate(file):
      if i >= 50:
        break
      if '-sdf' not in line:
        continue
      for part in line.split():
        if not part.startswith('-sdf'):
          continue
        sdf_parts = part.split(':')
        if len(sdf_parts) != 4:
          continue
        first_word = sdf_parts[1]
        file_path = sdf_parts[3]
        file_name = os.path.basename(file_path)
        file_name_parts = file_name.split('_')
        if len(file_name_parts) > 1:
          corner_name = file_name_parts[-1].split('.')[0] + first_word
          logger.info(f"[VCM] Found corner name '{corner_name}' in comp.log.")
          return corner_name
  logger.log(f"[VCM] Corner name not found in comp.log.", level="WARNING")
  return None


def check_sim_single_function_result(log_file='sim.log', exception_file='log_exception'):
  vtool_home = check_vtool_home()
    
  # 定义异常文件路径
  exception_file_path = os.path.join(vtool_home, 'tool', 'log', exception_file)

  # 获取异常内容
  exceptions = set()

  # 读取系统异常文件
  if os.path.isfile(exception_file_path):
    with open(exception_file_path, 'r') as ef:
      exceptions.update(line.strip() for line in ef)

  if os.path.exists(log_file) is False:
    print(f"[VCM] Error: Log file '{log_file}' not found.")
    return 0

  # 读取日志文件并检查错误
  count_error = 0
    
  with open(log_file, 'r') as log:
    for line in log:
      # 检查是否包含异常内容
      if any(exception in line for exception in exceptions):
        continue
            
      # 检查是否是错误信息
      if re.search(r'UVM_ERROR|\[ERROR\]|\[error\]|UVM_FATAL', line):
        count_error += 1

  return count_error

def check_sim_single_timing_result(file_path='sim.log', time_max_num=0):
  # 初始化计数器
  error_count = 0

  # 读取文件并检查时间违规
  with open(file_path, 'r') as log_file:
    for line in log_file:
      if "Timing violation" in line:
        error_count += 1

  # 输出结果
  if time_max_num == 0:
    error_out = error_count
  else:
    if error_count > time_max_num:
      error_out = error_count
    else:
      error_out = error_count - time_max_num

  return error_out

def get_node_info(part_name, part_mode, node_name):
  if part_mode == "multi":
    if part_name == "digit":
      nodes = ["digit01", "digit02", "digit03", "digit04"]
      return [
        {"node_name": n, "host_name": NODE_MAP.get(n)}
        for n in nodes
      ]
    elif part_name == "edas":
      nodes = ["eda"]
      return [
        {"node_name": n, "host_name": NODE_MAP.get(n)}
        for n in nodes
      ]
    else:
      print(f"[VCM] Error: part_name '{part_name}' illegal, at 'multi' mode only 'digit' is supported.")
  elif part_mode == "single":
    host = NODE_MAP.get(node_name)
    if host is None:
      print(f"[VCM] Error: node_name '{node_name}' not in NODE_MAP.")
    return [{"node_name": node_name, "host_name": host}]
  else:
    print(f"[VCM] Error: part_mode '{part_mode}' illegal, only 'single' or 'multi' is supported.")

def check_regr_comp_result(logger, part_name, part_mode, node_name, work_name):
  node_infos = get_node_info(part_name, part_mode, node_name)
  if not node_infos:
    print(f"[VCM] Error: No node information found for part_name '{part_name}', part_mode '{part_mode}', node_name '{node_name}'.")
    return False
  
  current_user = get_current_user()
  fail_num = 0
  
  for node in node_infos:
    node_dir = "/" + node["host_name"]
    work_path = os.path.join(node_dir, "work", current_user, work_name, "regr")
    comp_status_path = os.path.join(work_path, "vcm.comp.fail")
    comp_info_path = os.path.join(work_path, VCM_TASK_FILENAME)
    if os.path.exists(comp_status_path) is True:
      print(f"[VCM] Error: {comp_status_path} exists.")
      fail_num += 1
    
    if os.path.exists(comp_info_path) is False:
      print(f"[VCM] Error: {comp_info_path} not found.")
      fail_num += 1

  return fail_num == 0      


def check_regr_log_extract(base_path, timing_check=False, exception_files=None,  time_max_num=0):
  """
  查找并分析所有 case*test/case*/case*test_*.log 文件，输出名称、seed、error数量、fatal数量、log路径、finished、timing_violation_num。
  :param base_path: 搜索的根目录
  :param exception_files: 例外文件列表（可选）
  :param timing_check: 是否检查Timing violation
  :param time_max_num: Timing violation最大容忍数
  :return: 结果列表，每项为 dict，包含名称、seed、error数量、fatal数量、log路径、finished、timing_violation_num
  """

  exceptions = set()
  if exception_files:
    for ef in exception_files:
      if os.path.isfile(ef):
        with open(ef, 'r') as f:
          for line in f:
            exceptions.add(line.strip())

  pattern = os.path.join(base_path, "case*test", "case*", "case*test_*.log")
  log_files = glob(pattern, recursive=True)

  results = []
  for log_path in log_files:
    m = re.search(r'(case[^/]*test)/case[^/]*?/case[^/]*test_(\w+)\.log$', log_path)
    if not m:
      continue
    case_name = m.group(1)
    seed = m.group(2)

    error_count = 0
    finished = False
    lines_buffer = []
    timing_violation_num = 0

    with open(log_path, 'r', errors='ignore') as f:
      for line in f:
        lines_buffer.append(line)
        if len(lines_buffer) > 50:
          lines_buffer.pop(0)
        if any(exc in line for exc in exceptions):
          continue
        if re.search(r'UVM_FATAL|UVM_ERROR|\[ERROR\]|\[error\]', line):
          error_count += 1
        if timing_check and "Timing violation" in line:
          timing_violation_num += 1

    for l in lines_buffer:
      if "finish at simulation time" in l:
        finished = True
        break

    # 如果设置了最大容忍数，返回超出部分，否则返回总数
    if timing_check:
      if time_max_num > 0:
        timing_violation_num = max(0, timing_violation_num - time_max_num)

    results.append({
      'case_name': case_name,
      'case_seed': seed,
      'error_count': error_count,
      'log_path': log_path,
      'finished': finished,
      'timing_count': timing_violation_num if timing_check else None
    })

  return results

def get_sim_log_time(log_path):
  """
  从日志文件中提取时间信息。
  :param log_path: 日志文件路径
  :return: 提取的时间信息
  """
  time_info = []
  with open(log_path, 'r') as f:
    for line in f:
      if "Simulation time" in line:
        time_info.append(line.strip())
  return time_info