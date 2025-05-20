import os
import re
import random
from glob import glob
from constants import NODE_MAP, get_current_user,get_current_dir, VCM_TASK_FILENAME
from constants import check_vtool_home
import subprocess

def determine_regr_type(logger):
  """
  根据当前目录名判断回归类型。

  参数:
    logger: 日志记录对象，用于输出日志信息。

  返回:
    str 或 None: 回归类型（'eman'、'slurm' 或 None）。
  """
  current_dir_name = os.path.basename(get_current_dir())
  if current_dir_name.startswith(("sim_pre", "sim_post", "sim")):
    return None
  if current_dir_name.startswith("regr"):
    return "eman"
  if current_dir_name.startswith("slurm"):
    return "slurm"
  logger.log(f"[VCM] Unknown regr type '{current_dir_name}'. ", level="WARNING")
  return None
    
def check_comp_result(logger, log_file_path):
  """
  检查编译日志文件是否包含特定的完成标志。

  参数:
    logger: 日志记录对象。
    log_file_path: 日志文件路径。

  返回:
    bool: 是否检测到预期的模式。
  """
  # 定义正则表达式模式
  elaboration_pattern = r'Verdi KDB elaboration done'

  if not os.path.isfile(log_file_path):
    logger.log(f"Log file '{log_file_path}' does not exist.", level="ERROR")
    return False
  try:
    with open(log_file_path, 'r') as file:
      lines = file.readlines()
  except Exception as e:
    logger.log(f"Failed to read '{log_file_path}': {e}", level="ERROR")
    return False

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
  """
  从编译日志中提取corner名称。

  参数:
    logger: 日志记录对象。
    comp_log_path: 编译日志文件路径，默认为"comp.log"。

  返回:
    str 或 None: 提取到的corner名称，未找到则为None。
  """
  if not os.path.exists(comp_log_path):
    logger.error(f"[VCM] Error: Log file '{comp_log_path}' does not exist.")
    return None

  try:
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
  except Exception as e:
    logger.error(f"[VCM] Error reading '{comp_log_path}': {e}")
    return None
  logger.log(f"[VCM] Corner name not found in comp.log.", level="WARNING")
  return None


def check_sim_single_function_result(log_file='sim.log', exception_file='log_exception'):
  """
  检查仿真日志中的功能错误数量，忽略指定异常。

  参数:
    log_file: 仿真日志文件名，默认为'sim.log'。
    exception_file: 异常内容文件名，默认为'log_exception'。

  返回:
    int: 检测到的错误数量。
  """
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
  """
  检查仿真日志中的Timing violation数量。

  参数:
    file_path: 仿真日志文件路径，默认为'sim.log'。
    time_max_num: Timing violation最大容忍数，默认为0。

  返回:
    int: 超出容忍数的Timing violation数量。
  """
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
  """
  获取节点信息。

  参数:
    part_name: 部件名称（如'digit'或'edas'）。
    part_mode: 模式（'single'或'multi'）。
    node_name: 节点名称。

  返回:
    list: 节点信息字典列表。
  """
  if part_mode == "multi":
    if part_name == "digit":
      nodes = ["digit01", "digit02", "digit03", "digit04"]
    elif part_name == "edas":
      nodes = ["eda"]
    else:
      raise ValueError(f"[VCM] Error: part_name '{part_name}' illegal, at 'multi' mode only 'digit' or 'edas' is supported.")
    return [{"node_name": n, "host_name": NODE_MAP.get(n)} for n in nodes]
  elif part_mode == "single":
    host = NODE_MAP.get(node_name)
    if host is None:
      raise ValueError(f"[VCM] Error: node_name '{node_name}' not in NODE_MAP.")
    return [{"node_name": node_name, "host_name": host}]
  else:
    raise ValueError(f"[VCM] Error: part_mode '{part_mode}' illegal, only 'single' or 'multi' is supported.")

def check_regr_comp_result(logger, part_name, part_mode, node_name, work_name):
  """
  检查回归编译结果。

  参数:
    logger: 日志记录对象。
    part_name: 部件名称。
    part_mode: 模式。
    node_name: 节点名称。
    work_name: 工作目录名称。

  返回:
    bool: 检查是否全部通过。
  """
  
  try:
    node_infos = get_node_info(part_name, part_mode, node_name)
  except ValueError as e:
    logger.log(str(e), level="ERROR")
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

  参数:
    base_path: 搜索的根目录。
    timing_check: 是否检查Timing violation。
    exception_files: 例外文件列表（可选）。
    time_max_num: Timing violation最大容忍数。

  返回:
    list: 结果列表，每项为 dict，包含名称、seed、error数量、log路径、finished、timing_violation_num。
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

    try:
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
    except Exception as e:
      continue
    finished = any("finish at simulation time" in l for l in lines_buffer)

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

  参数:
    log_path: 日志文件路径。

  返回:
    list: 提取的时间信息列表。
  """
  time_info = []
  if not os.path.isfile(log_path):
    return time_info
  with open(log_path, 'r') as f:
    for line in f:
      if "Simulation time" in line:
        time_info.append(line.strip())
  return time_info

def get_job_status_name(job_id):
  # 查询 job 状态
  try:
    job_check = subprocess.check_output(
      ['sacct', '-n', '-j', job_id, '-o', 'state', '--noheader'],
      stderr=subprocess.STDOUT
    ).decode().strip().split('\n')[-1]

    job_check = job_check.replace(" ", "")
  except subprocess.CalledProcessError:
    print(f"[VCM] Job {job_id} does not exist")
    return 

  if job_check == "COMPLETED":
    job_node = subprocess.check_output(
      ['sacct', '-j', job_id, '--format=NodeList'],
      stderr=subprocess.STDOUT
    ).decode().strip().split('\n')[-1].replace(" ", "")
    job_status = "OK"
  else:
    job_node = ""
    job_status = "TODO"

  return job_status, job_node, job_check