from module.module_manager import ModuleManager
from constants import get_real_time
from utils.utils_format import print_table

def print_tasks_table(cursor, tasks):
  """
  美观地格式化打印任务列表。
  针对元组格式：(task_id, module_id, created_at, created_by, git_de, git_dv, is_regr, regr_id, node_name, is_post, corner_name)
  created_at 默认为UTC时间，显示时+8小时
  """
  module_manager = ModuleManager(cursor)

  if not tasks:
    print("[VCM] No tasks found.")
    return

  headers = [
    "ID", "Module", "Created at", "Created by", "Git DE", "Git DV",
    "Is REGR", "REGR ID", "Node Name", "Is POST", "Corner Name"
  ]

  def format_value(i, row):
    if i == 1:
      return module_manager.find_module_name_by_id(row[1]) or ""
    elif i == 2:
      try:
        return get_real_time(row[2])
      except Exception:
        return str(row[2]) if row[2] is not None else ""
    elif i == 6 or i == 9:
      return "✔" if row[i] else "X"
    else:
      return str(row[i]) if row[i] is not None else ""

  formatted_rows = [
    [format_value(i, row) for i in range(len(headers))]
    for row in tasks
  ]
  print_table(headers, formatted_rows)