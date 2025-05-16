from tabulate import tabulate
from project.project_manager import ProjectManager
from utils.utils_lib import fetch_with_headers, print_table
from constants import get_real_time

def generate_project_report(cursor, project_name: str):
  """
  生成并打印指定项目的详细报告。

  功能:
    获取并展示指定项目的详细信息、所有模块和用例，按表格格式输出。

  参数:
    cursor : 数据库游标对象。
    project_name (str): 项目名称。

  返回:
    None
  """
  # 获取项目详情
  sql = "SELECT * FROM projects WHERE project_name = ?"
  details, details_headers = fetch_with_headers(cursor, sql, (project_name.upper(),))
  if not details:
    print(f"No details found for project '{project_name}'")
    return

  # 获取模块
  sql = """
      SELECT m.* FROM modules m
      JOIN projects p ON m.project_id = p.project_id
      WHERE p.project_name = ?
  """
  modules, modules_headers = fetch_with_headers(cursor, sql, (project_name.upper(),))
  if not modules:
      print(f"No modules found for project '{project_name}'")
      return

  # 获取用例
  sql = "SELECT * FROM module_case_view WHERE project_name = ?"
  cases, cases_headers = fetch_with_headers(cursor, sql, (project_name.upper(),))
  if not cases:
      print(f"No cases found for project '{project_name}'")
      return

  print("Project Details:")
  print(tabulate(details, headers=details_headers, tablefmt="grid"))
  print("\nModules:")
  print(tabulate(modules, headers=modules_headers, tablefmt="grid"))
  print("\nCases:")
  print(tabulate(cases, headers=cases_headers, tablefmt="grid"))

def print_projects_table(projects):
  """
  美观地格式化打印项目列表。
  针对元组格式：(id, project_name, create_time, creator)
  create_time 默认为UTC时间，显示时+8小时
  """
  if not projects:
    print("[VCM] No projects found.")
    return

  headers = ["ID", "Project", "Created at", "Created by"]
  processed_projects = []
  for row in projects:
    row = list(row)
    try:
      row[2] = get_real_time(row[2])
    except Exception:
      pass
    processed_projects.append([str(row[i]) for i in range(4)])

  print_table(headers, processed_projects)