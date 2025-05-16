from constants import get_current_user
from case.case_manager import CaseManager
from sim.sim_manager import SimManager
from module.module_manager import ModuleManager
from utils.utils_lib import generate_html_report_with_chart
from tabulate import tabulate
from utils.utils_git import get_project_name, get_module_name

def handle_list_sim_info(cursor, args):
  case_manager = CaseManager(cursor)
  sim_manager = SimManager(cursor)
  module_manager = ModuleManager(cursor)

  project_name = get_project_name(args)
  module_name = get_module_name(args)
  current_user = get_current_user()

  #check user
  if args.user is None:
    sim_user = args.user
  else:
    sim_user = current_user

  #check case_name
  if args.case_name is None:
    print("[VCM] Error: Case name is required.")
    return
  else:
    module_id = module_manager.find_module_id_by_name(module_name)
    if case_manager.exist_case(args.case_name, module_id) is False:
      print(f"[VCM] Error: Case '{args.case_name}' does not exist under module '{module_name}'.")
      return

  rows, headers = sim_manager.query_sim_info(args.case_name, project_name, module_name, sim_user)

  if rows:
    table = [list(row) for row in rows]

    if args.output == 'html':
      generate_html_report_with_chart(table, headers)
      print("[VCM] HTML report generated: simulation_report.html")
    else:
      print(tabulate(table, headers, tablefmt="grid"))
      #输出到log
      with open("vcm_sim_report.log", "w") as f:
        f.write(tabulate(table, headers, tablefmt="grid"))
  else:
    print("[VCM] No simulation records found.")
