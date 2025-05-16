import argparse
from module.module_service import ModuleService
from constants import AUTH_CODE, get_current_user
from utils.utils_git import get_project_name, get_module_name
from module.module_report import print_modules_table

class ModuleCLI:
  def __init__(self, cursor, logger):
    """
    初始化 ModuleCLI 实例。

    参数:
      cursor: 数据库游标对象，用于数据库操作。
      logger: 日志记录器对象，用于记录日志信息。
    """

    self.cursor = cursor
    self.logger = logger
    self.service = ModuleService(cursor, logger)

  def add_module_subcommands(subparsers):
    """
    向 argparse 的 subparsers 添加模块相关的子命令。

    参数:
      subparsers: argparse 的 subparsers 对象。
    """

    commands = {
      "add": {
        "help": "Add a new module.",
        "usage": "%(prog)s [module_name]",
        "arguments": [
          ("module_name", "Name of the module", {"nargs": "?"})
        ]
      },
      "exist": {
        "help": "Check if a module exists.",
        "usage": "%(prog)s [module_name]",
        "arguments": [
          ("module_name", "Name of the module", {"nargs": "?"})
        ]
      },
      "rename": {
        "help": "Rename a module.",
        "usage": "%(prog)s <old_module_name> <new_module_name>",
        "arguments": [
          ("old_module_name", "Current name of the module"),
          ("new_module_name", "New name for the module")
        ]
      },
      "list": {
        "help": "list modules for a project.",
        "usage": "%(prog)s [project_name]",
        "arguments": [
          ("project_name", "Name of the project to list its modules", {"nargs": "?"})
        ]
      },
      "del": {
        "help": "Delete a module.",
        "usage": "%(prog)s <module_name>",
        "arguments": [
          ("module_name", "Name of the module to delete")
        ]
      }
    }

    for cmd, config in commands.items():
      parser = subparsers.add_parser(cmd, help=config["help"], usage=config["usage"])
      for arg in config["arguments"]:
        arg_name, arg_help, *arg_options = arg
        parser.add_argument(arg_name, help=arg_help, **(arg_options[0] if arg_options else {}))

  def _handle_rename(self, args):
    """
    处理模块重命名命令。

    参数:
      args: argparse 解析后的参数对象，包含 old_module_name 和 new_module_name。

    返回值:
      None
    """
    old_name = getattr(args, 'old_module_name', None)
    new_name = getattr(args, 'new_module_name', None)
    if not old_name or not new_name:
      print("[VCM] Error: Both old and new module names are required for rename.")
      return
    
    exists = self.service.module_exists(old_name)
    if not exists:
      print(f"[VCM] Error: Module '{old_name}' does not exist.")
      return

    if not self.service.rename_module(old_name, new_name):
      print("[VCM] Error: Old and new module names cannot be the same.")
      return
    print(f"[VCM] Module '{old_name}' renamed to '{new_name}'.")

  def _handle_add(self, args):
    """
    处理添加模块命令。

    参数:
      args: argparse 解析后的参数对象，包含项目名和模块名。

    返回值:
      None
    """
    project_name = get_project_name(args)
    module_name = get_module_name(args)
    
    self.service.add_module(project_name, module_name)
    #print(f"[VCM] Module '{module_name}' added under project '{project_name}'.")

  def _handle_exist(self, args):
    """
    检查模块是否存在。

    参数:
      args: argparse 解析后的参数对象，包含模块名。

    返回值:
      None
    """
    module_name = get_module_name(args)
    exists = self.service.module_exists(module_name)

    print(f"[VCM] Module '{module_name}' {'exists' if exists else 'does not exist'}.")

  def _handle_list(self, args):
    """
    列出指定项目下的所有模块。

    参数:
      args: argparse 解析后的参数对象，包含项目名。

    返回值:
      None
    """
    project_name = get_project_name(args)
    modules = self.service.list_modules(project_name)

    if modules:
      print_modules_table(self.cursor, modules)
    else:
      print(f"[VCM] No modules found for project '{project_name}'.")

  def _handle_del(self, args):
    """
    处理删除模块命令，需输入授权码。

    参数:
      args: argparse 解析后的参数对象，包含模块名。

    返回值:
      None
    """
    try:
      input_code = input("[VCM] Please enter authorization code to delete the module: ")
    except Exception:
      print("[VCM] Error: Failed to read input.")
      return
    
    if input_code != AUTH_CODE:
      print("[VCM] Invalid authorization code. Module deletion aborted.")
      return
    
    module_name = get_module_name(args)
    
    success = self.service.delete_module(module_name)

    if not success:
      print(f"[VCM] Module '{module_name}' does not exist.")
      return
    
    print(f"[VCM] Module '{module_name}' has been deleted.")

  def handle_module_commands(self, args):
    """
    处理模块相关的命令行子命令。
    """
    sub = getattr(args, 'subcommand', None)
    if not sub:
      print("[VCM] Error: No subcommand provided. Use 'module -h' for help.")
      return

    if sub == 'add':
      self._handle_add(args)
    elif sub == 'rename':
      self._handle_rename(args)
    elif sub == 'exist':
      self._handle_exist(args)
    elif sub == 'list':
      self._handle_list(args)
    elif sub == 'del':
      self._handle_del(args)
    else:
      print(f"[VCM] Unknown module command '{sub}', please use 'module -h'")