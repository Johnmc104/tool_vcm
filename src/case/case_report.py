from tabulate import tabulate
from utils.utils_format import fetch_with_headers
from case.case_manager import CaseManager
from module.module_manager import ModuleManager
from constants import get_real_time
from utils.utils_format import print_table

def generate_case_report(cursor, module_name: str) -> None:
  """
  生成并打印指定模块的用例报告。

  参数:
    manager: 管理器实例，需有 cursor 属性。
    module_name (str): 模块名称。

  返回:
    None
  """
  # 获取用例
  sql = "SELECT * FROM module_case_view WHERE module_name = ?"
  cases, headers = fetch_with_headers(cursor, sql, (module_name,))
  if not cases:
    print(f"[VCM] No cases found for module '{module_name}'.")
    return None
  print("Cases:")
  print(tabulate(cases, headers=headers, tablefmt="grid"))
  return cases

def print_cases_table(cursor, cases):
  """
  美观地格式化打印用例列表。
  针对元组格式：(case_id, module_id, created_at, created_by, case_name, case_c_name, case_c_group, support_st, support_bt, support_regr, support_post, support_ams)
  created_at 默认为UTC时间，显示时+8小时
  """
  module_manager = ModuleManager(cursor)

  if not cases:
    print("[VCM] No cases found.")
    return

  headers = [
    "ID", "Module", "Created at", "Created by", "Case Name", "Case C Name",
    "Case Group", "ST", "BT", "REGR", "POST", "AMS"
  ]

  def format_value(i, row):
    if i == 1:
      return module_manager.find_module_name_by_id(row[1]) or ""
    elif i == 2:
      try:
        return get_real_time(row[2])
      except Exception:
        return str(row[2]) if row[2] is not None else ""
    elif i in [7, 8, 9, 10, 11]:
      return "✔" if row[i] else "X"
    else:
      return str(row[i]) if row[i] is not None else ""

  # 格式化所有行，便于计算最大宽度
  formatted_rows = [
    [format_value(i, row) for i in range(len(headers))]
    for row in cases
  ]
  print_table(headers, formatted_rows)