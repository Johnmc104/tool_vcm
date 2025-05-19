import argparse
from project.project_manager import ProjectManager
from project.project_service import ProjectService
from utils.utils_git import get_project_name
from project.project_report import print_projects_table

class ProjectCLI:
  """
  命令行解析层，负责参数解析与交互。
  """
  def __init__(self, cursor, logger):
    self.service = ProjectService(cursor, logger)
    self.logger = logger

  @staticmethod
  def add_project_subcommands(subparsers):
    commands = {
      "add": {
        "help": "Add a new project.",
        "usage": "%(prog)s [project_name]",
        "arguments": [
          ("project_name", "Name of the project", {"nargs": "?"})
        ]
      },
      "exist": {
        "help": "Check if a project exists.",
        "usage": "%(prog)s [project_name]",
        "arguments": [
          ("project_name", "Name of the project", {"nargs": "?"})
        ]
      },
      "rename": {
        "help": "Rename a project.",
        "usage": "%(prog)s <old_project_name> <new_project_name>",
        "arguments": [
          ("old_project_name", "Current project name"),
          ("new_project_name", "New project name")
        ]
      },
      "list": {
        "help": "List all projects.",
        "usage": "%(prog)s",
        "arguments": []
      },
      "report": {
        "help": "Generate a project report.",
        "usage": "%(prog)s [project_name]",
        "arguments": [
          ("project_name", "Name of the project", {"nargs": "?"})
        ]
      },
      "del": {
        "help": "Delete a project (requires authorization).",
        "usage": "%(prog)s <project_name>",
        "arguments": [
          ("project_name", "Name of the project to delete")
        ]
      }
    }
    for cmd, config in commands.items():
      parser = subparsers.add_parser(cmd, help=config["help"], usage=config["usage"])
      for arg in config["arguments"]:
        arg_name, arg_help, *arg_options = arg
        parser.add_argument(arg_name, help=arg_help, **(arg_options[0] if arg_options else {}))

  def handle_project_commands(self, args):
    """
    处理项目相关的命令行操作。

    功能:
      根据子命令执行对应的项目操作，如添加、查询、重命名、删除、列出和生成报告等。

    参数:
      args: 命令行参数对象。

    返回:
      None
    """
        
    sub = getattr(args, 'subcommand', None)
    if not sub:
      self.logger.log("No subcommand provided. Use 'project -h' for help.", level="ERROR")
      return

    if sub == 'add':
      project_name = get_project_name(args)
      if project_name is None:
        self.logger.log("Project name is required.", level="ERROR")
        return
      
      self.service.add_project(project_name)

    elif sub == 'exist':
      project_name = get_project_name(args)
      if not project_name:
        return
      self.service.exist_project(project_name)

    elif sub == 'rename':
      old_name = getattr(args, 'old_project_name', None)
      new_name = getattr(args, 'new_project_name', None)
      if not old_name or not new_name:
        self.logger.log("Both old and new project names are required.", level="ERROR")
        return
      self.service.rename_project(old_name, new_name)

    elif sub == 'list':
      ok, result = self.service.list_projects()
      if not ok:
        self.logger.log("Failed to list projects.", level="ERROR")
        return
      else:
        print_projects_table(result)

    elif sub == 'report':
      project_name = get_project_name(args)
      if not project_name:
        return
      self.service.report_project(project_name)

    elif sub == 'del':
      project_name = get_project_name(args)
      if not project_name:
        self.logger.log("Project name is required.", level="ERROR")
        return
      input_code = input("Please enter authorization code to delete the project: ")
      self.service.delete_project(project_name, input_code)

    else:
      self.logger.log("Unknown project command.", level="ERROR")