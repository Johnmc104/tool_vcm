from tabulate import tabulate
from project.project_manager import ProjectManager
from constants import get_real_time
from utils.utils_lib import print_table

def print_modules_table(cursor, modules):
  """
  美观地格式化打印项目列表。
  针对元组格式：(id, module_name, project_id, create_time, creator)
  create_time 默认为UTC时间，显示时+8小时
  """
  manager = ProjectManager(cursor)

  if not modules:
    print("[VCM] No modules found.")
    return

  headers = ["ID", "Module", "Project", "Created at", "Created by"]

  def format_row(row):
    # 生成格式化后的行
    formatted = [
      str(row[0]) if row[0] is not None else "",
      str(row[1]) if row[1] is not None else "",
      str(manager.find_project_name_by_id(row[2]) or ""),
      get_real_time(row[3]) if row[3] is not None else "",
      str(row[4]) if row[4] is not None else "",
    ]
    return formatted

  formatted_rows = [format_row(row) for row in modules]
  print_table(headers, formatted_rows)