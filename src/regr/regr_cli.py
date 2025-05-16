from regr.regr_service import RegrService
from utils.utils_git import get_module_name
from constants import get_current_user, get_current_dir
from regr.regr_report import print_regrs_table

class RegrCLI:
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.logger = logger
    self.service = RegrService(cursor, logger)
    
  @staticmethod
  def add_regr_subcommands(subparsers):
    """
    向命令行解析器添加回归相关的子命令。

    参数:
      subparsers: argparse 的 subparsers 对象，用于注册子命令。
    """
    commands = {
      "add": {
        "help": "Add a new regression record.",
        "usage": "%(prog)s <regr_type> [module_name] ",
        "arguments": [
          ("regr_type", "Regression type"),
          ("module_name", "Module name", {"nargs": "?"})
        ]
      },
      "update_slurm_info": {
        "help": "Add SLURM information to a regression record.",
        "usage": "%(prog)s <part_name> <part_mode> <node_name> <work_name> <work_url> <case_list> [module_name]",
        "arguments": [
          ("part_name", "Partition name"),
          ("part_mode", "Partition mode"),
          ("node_name", "Node name"),
          ("work_name", "work name"),
          ("work_url", "work URL"),
          ("case_list", "Case list (comma separated)"),
          ("module_name", "Module name", {"nargs": "?"})
        ]
      },
      "exist": {
        "help": "Check if a regression record exists.",
        "usage": "%(prog)s <regr_id> [module_name]",
        "arguments": [
          ("regr_id", "Regression ID"),
          ("module_name", "Module name", {"nargs": "?"})
        ]
      },
      "list": {
        "help": "List all regression records for a module.",
        "usage": "%(prog)s [module_name]",
        "arguments": [
          ("module_name", "Module name", {"nargs": "?"})
        ]
      },
      "del": {
        "help": "Delete a regression record.",
        "usage": "%(prog)s <regr_id> [module_name]",
        "arguments": [
          ("regr_id", "Regression ID"),
          ("module_name", "Module name", {"nargs": "?"})
        ]
      }
    }

    for cmd, config in commands.items():
      parser = subparsers.add_parser(cmd, help=config["help"], usage=config["usage"])
      for arg in config["arguments"]:
        arg_name, arg_help, *arg_options = arg
        parser.add_argument(arg_name, help=arg_help, **(arg_options[0] if arg_options else {}))

  def handle_regr_commands(self, args):
    module_name = get_module_name(args)

    if args.subcommand == 'add':
      regr_base = get_current_dir()
      self.service.add_regr(
        regr_base, args.regr_type, module_name
      ) 

    elif args.subcommand == 'update_slurm_info':
      self.service.update_slurm_info(
        args.part_name, args.part_mode,
        args.node_name, args.work_name, args.work_url,
        args.case_list, module_name
      )
    elif args.subcommand == 'exist':
      self.service.exist(int(args.regr_id), module_name)
    elif args.subcommand == 'list':
      regrs = self.service.list_regrs(module_name)
      if regrs:
        print_regrs_table(self.cursor,regrs)
      else:
        print("[VCM] No regression records found.")
    elif args.subcommand == 'del':
      self.service.delete(int(args.regr_id), module_name)
    else:
      print("[VCM] Unknown regr command. Use 'regr -h' for help.")