import argparse
from db_manager import db_connection, init_database
from project.project_cli import ProjectCLI
from module.module_cli import ModuleCLI
from case.case_cli import CaseCLI
from regr.regr_cli import RegrCLI
from task.task_cli import TaskCLI
from sim.sim_cli import SimCLI
from info.info_cli import InfoCLI

class VcmCLI: 
  def __init__(self, cursor):
    self.cursor = cursor

  def parse_cmd():
    title_str = (
      "       Verification Case Management System (VCM)\n"
      "            Version 1.3.0 May 16 2025 \n"
      "                    by zhhe\n"
    )

    parser = argparse.ArgumentParser(
      description=title_str,
      formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.3.0")
    parser.add_argument("-debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
      "-l", "--level", type=str, default="INFO",
      choices=["DEBUG", "INFO", "WARNING", "ERROR"],
      help="Set log level (DEBUG, INFO, WARNING, ERROR)"
    )

    subparsers = parser.add_subparsers(dest='command')

    # subparsers
    subparsers.add_parser('init', help="Initialize the project and module")

    db_parser = subparsers.add_parser('db', help="Database management")
    db_subparsers = db_parser.add_subparsers(dest='subcommand')
    db_subparsers.add_parser('init', help="Initialize the database")

    project_parser = subparsers.add_parser('project', help="Project management")
    project_subparsers = project_parser.add_subparsers(dest='subcommand')
    ProjectCLI.add_project_subcommands(project_subparsers)

    module_parser = subparsers.add_parser('module', help="Module management")
    module_subparsers = module_parser.add_subparsers(dest='subcommand')
    ModuleCLI.add_module_subcommands(module_subparsers)

    case_parser = subparsers.add_parser('case', help="Case management")
    case_subparsers = case_parser.add_subparsers(dest='subcommand')
    CaseCLI.add_case_subcommands(case_subparsers)

    regr_parser = subparsers.add_parser('regr', help="Regression management")
    regr_subparsers = regr_parser.add_subparsers(dest='subcommand')
    RegrCLI.add_regr_subcommands(regr_subparsers)

    task_parser = subparsers.add_parser('task', help="Task management")
    task_subparsers = task_parser.add_subparsers(dest='subcommand')
    TaskCLI.add_task_subcommands(task_subparsers)

    sim_parser = subparsers.add_parser('sim', help="Simulation management")
    sim_subparsers = sim_parser.add_subparsers(dest='subcommand')
    SimCLI.add_sim_subcommands(sim_subparsers)

    info_parser = subparsers.add_parser('info', help="Info management")
    info_subparsers = info_parser.add_subparsers(dest='subcommand')
    InfoCLI.add_info_subcommands(info_subparsers)

    return parser
     