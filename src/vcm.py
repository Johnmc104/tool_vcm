import os
from db_manager import db_connection, init_database
from utils.utils_lib import get_db_name, create_db_file
from utils.utils_log import Logger
from vcm_cli import VCMCLI
from project.project_cli import ProjectCLI
from module.module_cli import ModuleCLI
from case.case_cli import CaseCLI
from regr.regr_cli import RegrCLI
from task.task_cli import TaskCLI
from sim.sim_cli import SimCLI
from info.info_cli import InfoCLI
from utils.utils_git import get_project_and_module_name

def parse_args(args, cursor, logger, db_name, debug=False):
  # print(f"[VCM] command: {args.command}")
  if args.command == 'init':
    cli_project = ProjectCLI(cursor, logger)
    cli_module = ModuleCLI(cursor, logger)
    project_name, module_name = get_project_and_module_name()
    cli_project.service.add_project(project_name)
    cli_module.service.add_module(project_name, module_name)
  elif args.command == 'db':
    if getattr(args, 'subcommand', None) == 'init':
      create_db_file(cursor, db_name)
  elif args.command == 'project':
    cli_project = ProjectCLI(cursor, logger)
    cli_project.handle_project_commands(args)
  elif args.command == 'module':
    cli_module = ModuleCLI(cursor, logger)
    cli_module.handle_module_commands(args)
  elif args.command == 'case':
    cli_case = CaseCLI(cursor, logger)
    cli_case.handle_case_commands(args)
  elif args.command == 'regr':
    cli_regr = RegrCLI(cursor, logger)
    cli_regr.handle_regr_commands(args)
  elif args.command == 'task':
    cli_task = TaskCLI(cursor, logger)
    cli_task.handle_task_commands(args)
  elif args.command == 'sim':
    cli_sim = SimCLI(cursor, logger)
    cli_sim.handle_sim_commands(args)
  elif args.command == 'info':
    cli_info = InfoCLI(cursor, logger)
    cli_info.handle_info_commands(args)
  else:
    print("[VCM] Unknown command. Use '-h' for help.")

if __name__ == "__main__":
  
  parser = VCMCLI.parse_cmd()
  args = parser.parse_args()

  logger = Logger()

  #if args.debug:
  #  print("Debug mode enabled")
  #else:
  #  print("Debug mode disabled")
  #print(f"Log level set to {args.level}")

  db_dir, db_name = get_db_name(debug=args.debug)
  logger.log(f"Database directory: {db_name}", level="DEBUG")

  if args.command is None:
    parser.print_help()
    exit(0)
    
  with db_connection(db_name) as conn:
    cursor = conn.cursor()
    parse_args(args, cursor, logger, db_name, debug=args.debug)