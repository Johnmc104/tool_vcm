import os
import re
from typing import List

def find_case_uvm_dir():
  """
  功能描述:
    查找当前目录或父目录下的 case_uvm 文件夹路径。

  参数:
    无

  返回值:
    str 或 None: 返回 case_uvm 文件夹的绝对路径，未找到则返回 None。
  """
  current_dir = os.getcwd()
  parent_dir = os.path.dirname(current_dir)
  for path in [os.path.join(current_dir, "case_uvm"), os.path.join(parent_dir, "case_uvm")]:
    if os.path.isdir(path):
      return path
  print("[VCM] Error, case_uvm folder not found in current or parent directory.")
  return None

def find_case_sw_info(case_name):
  """
  功能描述:
    查找指定 case_name 的 SystemVerilog 文件，并提取 group_name 和 case_c_name。

  参数:
    case_name (str): 用例名称。

  返回值:
    tuple: (group_name, case_c_name)，均为 str 或 None。
  """
  target_dir = find_case_uvm_dir()
  if not target_dir or not os.path.isdir(target_dir):
    print(f"[VCM] Error, {target_dir} folder not exists")
    return None, None

  for root, _, files in os.walk(target_dir):
    if f"{case_name}.sv" in files:
      file_path = os.path.join(root, f"{case_name}.sv")
      with open(file_path, "r") as f:
        content = f.read()
      class_match = re.search(r"class\s+(\w+)\s+extends", content)
      params_match = re.search(r'bin\("([^"]*)".*?"([^"]*)"', content)
      if class_match and class_match.group(1) == case_name:
        group_name = params_match.group(1) if params_match else None
        case_c_name = params_match.group(2) if params_match else None
        print(f"[VCM] Group_Name: {group_name}, Case_Name: {case_c_name}")
        return group_name, case_c_name
      else:
        print(f"[VCM] Error, class_name not found in file: {file_path}")
  return None, None

def find_case_hw_info(file_path: str = "sim.log"):
  """
  功能描述:
    从仿真日志文件首行提取用例名称和随机种子。

  参数:
    file_path (str): 日志文件路径，默认 "sim.log"。

  返回值:
    tuple: (case_name, case_seed)，均为 str 或 None。
  """
  if not os.path.isfile(file_path):
    print(f"[VCM] Error, {file_path} not found.")
    return None, None

  # 打开文件并只读取第一行
  with open(file_path, "r") as file:
    first_line = file.readline().strip() # 读取第一行并去掉两端多余的空白字符

  # 使用正则表达式提取参数内容
  seed_match = re.search(r'\+ntb_random_seed=(\d+)', first_line)
  testname_match = re.search(r'\+UVM_TESTNAME=([a-zA-Z0-9_]+)', first_line)

  # 获取匹配的内容
  case_seed = seed_match.group(1) if seed_match else None
  case_name = testname_match.group(1) if testname_match else None

  return case_name, case_seed

def find_regr_cfg_list_path(filename: str = "case_list.txt"):
  """
  功能描述:
    智能查找 regr_cfg 目录下的 case_list.txt 文件路径，若无则返回当前目录下的文件路径。

  参数:
    filename (str): 文件名，默认 "case_list.txt"。

  返回值:
    str: 文件的绝对路径。
  """
  current_dir = os.getcwd()
  parent_dir = os.path.dirname(current_dir)
  regr_cfg_current = os.path.join(current_dir, "regr_cfg")
  regr_cfg_parent = os.path.join(parent_dir, "regr_cfg")
  if os.path.isdir(regr_cfg_current):
    return os.path.join(regr_cfg_current, filename)
  elif os.path.isdir(regr_cfg_parent):
    return os.path.join(regr_cfg_parent, filename)
  else:
    return os.path.join(current_dir, filename)

def get_cases_name_from_list(case_list_filename: str = "case_list.txt"):
  """
  功能描述:
    根据当前路径结构智能查找 case_list.txt 文件并提取用例名称。

  参数:
    case_list_filename (str): 用例列表文件名，默认 "case_list.txt"。

  返回值:
    list: 用例名称列表。
  """
  case_list_path = find_regr_cfg_list_path(case_list_filename)

  case_list = []
  if not os.path.isfile(case_list_path):
    print(f"[VCM] Error, {case_list_path} not found.")
    return case_list

  with open(case_list_path, "r") as file:
    for line in file:
      line = line.strip()
      if line and not line.startswith("#"):
        case_list.append(line)
  # 去重并保持顺序
  case_list = list(dict.fromkeys(case_list))
  return case_list

def check_case_file_exist(case_name: str):
  """
  功能描述:
    检查单个 case 文件（case_name.sv）是否存在于 case_uvm 目录（支持多层子目录）下。

  参数:
    case_name (str): 用例名称。

  返回值:
    bool: 是否存在。
  """
  case_dir = find_case_uvm_dir()
  if not case_dir:
    print("[VCM] Error, case_uvm directory not found.")
    return False

  #print(f"[VCM] Searching for {case_name}.sv in {case_dir}")
  for root, _, files in os.walk(case_dir):
    for file in files:
      #print(f"[VCM] {file} found in {root}")
      if file == f"{case_name}.sv":
        #print(f"[VCM] {case_name}.sv found in {root}")
        return True
  #print(f"[VCM] {case_name}.sv not found in {case_dir}")
  return False

def check_case_files_exist(case_names: List[str]):
  """
  功能描述:
    检查给定的 case 名称列表中，每个 case 文件（case_name.sv）是否存在于 case_uvm 目录（支持多层子目录）下。

  参数:
    case_names (list[str]): 用例名称列表。

  返回值:
    dict[str, bool]: key 为 case 名称，value 为是否存在（True/False）。
  """
  case_dir = find_case_uvm_dir()
  if not case_dir:
    print("[VCM] Error, case_uvm directory not found.")
    return {name: False for name in case_names}

  # 构建所有case文件名集合
  case_files_set = set()
  for root, _, files in os.walk(case_dir):
    for file in files:
      if file.endswith(".sv"):
        case_name = os.path.splitext(file)[0]
        case_files_set.add(case_name)

  result = {}
  for name in case_names:
    result[name] = name in case_files_set
  return result

def check_case_name_valid(case_name: str):
  """
  功能描述:
    检查用例名称是否符合命名规范：必须为 case_*_test 这种格式。

  参数:
    case_name (str): 用例名称。

  返回值:
    bool: 是否符合命名规范。
  """
  # 必须以 case_ 开头，_test 结尾，中间至少有一个字符，可为字母、数字、下划线
  return bool(re.match(r"^case_[a-zA-Z0-9_]+_test$", case_name))
  
def get_info_from_emc(emc_file: str = "emc.txt"):
  """
  功能描述:
    解析 EMC 配置文本，返回结构化的测试用例数据。
    每个测试用例组为一个 dict，包含 names, count, arguments, tags 等字段。

  参数:
    emc_file (str): EMC 配置文件名，默认 "emc.txt"。

  返回值:
    list: 每个元素为 dict，包含 names, count, arguments, tags。
  """
  emc_file_path = find_regr_cfg_list_path(emc_file)
  if not os.path.isfile(emc_file_path):
    print(f"[VCM] Error, {emc_file_path} not found.")
    return []

  with open(emc_file_path, "r") as f:
    lines = f.readlines()

  # 找到 tests: 行号
  tests_idx = next((idx for idx, line in enumerate(lines) if re.match(r'^\s*tests\s*:', line)), None)
  if tests_idx is None:
    print("[VCM] Error, 'tests:' section not found.")
    return []

  emc_info = []
  i = tests_idx + 1
  while i < len(lines):
    line = lines[i]
    if re.match(r'^\s*#', line) or not line.strip():
      i += 1
      continue
    name_match = re.match(r'^\s*-\s*name\s*:\s*(.+)', line)
    if name_match:
      names = [n.strip() for n in name_match.group(1).split(',')]
      test_info = {
        "names": names,
        "count": 1,
        "arguments": None,
        "tags": None,
      }
      j = i + 1
      while j < len(lines):
        next_line = lines[j]
        # 如果遇到下一个 - name: 或空行或非缩进行，结束本组
        if re.match(r'^\s*-\s*name\s*:', next_line) or not next_line.strip() or not next_line.startswith(' '):
          break
        count_match = re.match(r'^\s*count\s*:\s*(\d+)', next_line)
        if count_match:
          test_info["count"] = int(count_match.group(1))
        arg_match = re.match(r'^\s*arguments\s*:\s*(.+)', next_line)
        if arg_match:
          test_info["arguments"] = arg_match.group(1).strip()
        tags_match = re.match(r'^\s*tags\s*:\s*(.+)', next_line)
        if tags_match:
          test_info["tags"] = tags_match.group(1).strip()
        j += 1
      emc_info.append(test_info)
      i = j
    else:
      i += 1
  return emc_info

def gen_case_list_from_emc(emc_file: str = "emc.txt"):
  """
  功能描述:
    根据结构化测试用例数据，生成最终的 case 名称列表（按 count 展开），并写入 .list 文件。

  参数:
    emc_file (str): EMC 配置文件名，默认 "emc.txt"。

  返回值:
    无
  """

  emc_info = get_info_from_emc(emc_file)
  emc_file_path = find_regr_cfg_list_path(emc_file)
  case_list = []

  for info_item in emc_info:
    count = info_item.get("count", 1)
    for name in info_item["names"]:
      case_list.extend([name] * count)
  
  list_name = emc_file_path.rsplit('.', 1)[0] + '.list'
  list_file_path = os.path.join(os.path.dirname(emc_file_path), list_name)

  with open(list_file_path, "w") as f:
    for case in case_list:
      f.write(f"{case}\n")
  print(f"[VCM] Case list generated: {list_file_path}")

def caselist_lint(caselist_name: str, module_name: str = None):
  """
  功能描述:
    检查 case list 文件中的用例名称是否合法且对应文件存在。

  参数:
    caselist_name (str): case list 文件名。
    module_name (str): 模块名称，可选。

  返回值:
    tuple: (cases, status)
      cases (list): 用例名称列表。
      status (bool): 检查是否全部通过。
  """
  # Check if the case list name is valid
  cases = get_cases_name_from_list(caselist_name)
  if not cases:
    print(f"[VCM] Error: Case list '{caselist_name}' does not exist.")
    return [], False
  
  status = True
  for case_name in cases:
    # Check if the case name is valid
    if check_case_name_valid(case_name) is False:
      print(f"[VCM] Error: Case '{case_name}' is not valid.")
      status = False
      continue
    # Check if the case file exists
    if check_case_file_exist(case_name) is False:
      print(f"[VCM] Error: Case '{case_name}' does not exist in work_dir '{module_name}'.")
      status = False
      continue
  
  return cases, status