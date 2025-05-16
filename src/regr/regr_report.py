from module.module_manager import ModuleManager
from utils.utils_lib import print_table

def print_regrs_table(cursor, regrs, max_count=None):
  """
  美观地格式化打印回归(regrs)列表。
  针对元组格式：(regr_id, module_id, created_at, created_by, regr_base, regr_type, part_name, part_mode, node_name, project_name, project_url, case_list)
  参数:
    cursor: 数据库游标
    regrs: 回归记录列表
    max_count: 最多打印多少条记录（None为全部）
  """
  module_manager = ModuleManager(cursor)

  if not regrs:
    print("[VCM] No regrs found.")
    return

  headers = [
    "ID", "Module", "Created at", "Created by", "Base", "Type",
    "Part Name", "Part Mode", "Node", "Project", "URL", "Case List"
  ]

  def format_value(i, row):
    if i == 1:
      return module_manager.find_module_name_by_id(row[1]) or ""
    else:
      return str(row[i]) if row[i] is not None else ""

  # 格式化所有行，便于计算最大宽度
  display_regrs = regrs if max_count is None else regrs[:max_count]
  formatted_rows = [
    [format_value(i, row) for i in range(len(headers))]
    for row in display_regrs
  ]
  print_table(headers, formatted_rows)