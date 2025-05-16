import sys
from db_manager import db_connection
from utils.utils_lib import get_db_name, create_db_file
from utils.utils_log import Logger
from utils.utils_git import get_project_and_module_name_from_git
from utils.utils_env import check_vtool_home
from vcm_cli import VcmCLI
from project.project_cli import ProjectCLI
from module.module_cli import ModuleCLI
from case.case_cli import CaseCLI
from regr.regr_cli import RegrCLI
from task.task_cli import TaskCLI
from sim.sim_cli import SimCLI
from info.info_cli import InfoCLI


def parse_args(args, cursor, logger, db_name, debug=False):
  command_map = {
    'project': lambda: ProjectCLI(cursor, logger).handle_project_commands(args),
    'module' : lambda: ModuleCLI(cursor, logger).handle_module_commands(args),
    'case'   : lambda: CaseCLI(cursor, logger).handle_case_commands(args),
    'regr'   : lambda: RegrCLI(cursor, logger).handle_regr_commands(args),
    'task'   : lambda: TaskCLI(cursor, logger).handle_task_commands(args),
    'sim'    : lambda: SimCLI(cursor, logger).handle_sim_commands(args),
    'info'   : lambda: InfoCLI(cursor, logger).handle_info_commands(args),
  }

  if args.command == 'init':
    # Initialize the project and module name, auto create them
    # based on the current git repository
    cli_project = ProjectCLI(cursor, logger)
    cli_module = ModuleCLI(cursor, logger)
    project_name, module_name = get_project_and_module_name_from_git()
    cli_project.service.add_project(project_name)
    cli_module.service.add_module(project_name, module_name)
  elif args.command == 'db':
    if hasattr(args, 'subcommand') and args.subcommand == 'init':
      create_db_file(cursor, db_name)
  elif args.command in command_map:
    command_map[args.command]()
  else:
    print("[VCM] Unknown command. Use '-h' for help.")

if __name__ == "__main__":
  vtool_home = check_vtool_home()

  parser = VcmCLI.parse_cmd()
  args = parser.parse_args()

  logger = Logger()

  db_dir, db_name = get_db_name(debug=getattr(args, "debug", False))
  logger.log(f"Database file: {db_name}", level="DEBUG")

  if args.command is None:
    parser.print_help()
    sys.exit(0)

  with db_connection(db_name) as conn:
    cursor = conn.cursor()
    parse_args(args, cursor, logger, db_name, debug=getattr(args, "debug", False))