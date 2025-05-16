from case.case_service import CaseService
from utils.utils_git import get_module_name
from constants import AUTH_CODE

class CaseCLI:
  def __init__(self, cursor, logger):
    self.service = CaseService(cursor, logger)

  @staticmethod
  def add_case_subcommands(subparsers):
    """
    向命令行解析器添加用例相关的子命令。

    参数:
        subparsers: argparse 的 subparsers 对象，用于注册子命令。
    """
    commands = {
      "add_bt": {
        "help": "Add a new BT case.",
        "usage": "%(prog)s <case_name> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to add"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "add_st": {
        "help": "Add a new ST case.",
        "usage": "%(prog)s <case_name> <case_c_name> <case_c_group> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to add"),
          ("case_c_name", "Chinese name for the case"),
          ("case_c_group", "Chinese group for the case"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "exist": {
        "help": "Check if a case exists.",
        "usage": "%(prog)s <case_name> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to check"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "rename": {
        "help": "Rename a case.",
        "usage": "%(prog)s <old_case_name> <new_case_name> [module_name]",
        "arguments": [
          ("old_case_name", "Current name of the case"),
          ("new_case_name", "New name for the case"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "list": {
        "help": "list cases for a given module.",
        "usage": "%(prog)s [module_name]",
        "arguments": [
          ("module_name", "Module name for which to list cases", {"nargs": "?"})
        ]
      },
      "report": {
        "help": "Generate a case report for a given module.",
        "usage": "%(prog)s [module_name]",
        "arguments": [
          ("module_name", "Module name for which to generate the case report", {"nargs": "?"})
        ]
      },
      "del": {
        "help": "Delete a case. (Requires authorization)",
        "usage": "%(prog)s <case_name> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to delete"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "update_flag_bt": {
        "help": "Update support_bt flag for a case.",
        "usage": "%(prog)s <case_name> <support_bt> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to update"),
          ("support_bt", "Flag (True/False) to indicate support_bt"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "update_flag_st": {
        "help": "Update support_st flag for a case.",
        "usage": "%(prog)s <case_name> <support_st> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to update"),
          ("support_st", "Flag (True/False) to indicate support_st", {"choices": ["True", "False"]}),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"}),
        ]
      },
      "update_flag_st_info": {
        "help": "Update case_c_name and case_c_group for a case.",
        "usage": "%(prog)s <case_name> <case_c_name> <case_c_group> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to update"),
          ("case_c_name", "Chinese name for the case"),
          ("case_c_group", "Chinese group for the case"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"}),
        ]
      },
      "update_flag_regr": {
        "help": "Update support_regr flag for a case.",
        "usage": "%(prog)s <case_name> <support_regr> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to update"),
          ("support_regr", "Flag (True/False) to indicate support_regr"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "update_flag_post": {
        "help": "Update support_post flag for a case.",
        "usage": "%(prog)s <case_name> <support_post> [module_name]",
        "arguments": [
          ("case_name", "Name of the case to update"),
          ("support_post", "Flag (True/False) to indicate support_post"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      },
      "update_flag_ams": {
        "help": "Update support_ams flag for a case.",
        "usage": "%(prog)s <case_name> <support_ams> [module_name] ",
        "arguments": [
          ("case_name", "Name of the case to update"),
          ("support_ams", "Flag (True/False) to indicate support_ams"),
          ("module_name", "Module name that the case belongs to", {"nargs": "?"})
        ]
      }
    }

    for cmd, config in commands.items():
      parser = subparsers.add_parser(cmd, help=config["help"], usage=config["usage"])
      for arg in config["arguments"]:
        arg_name, arg_help, *arg_options = arg
        parser.add_argument(arg_name, help=arg_help, **(arg_options[0] if arg_options else {}))

  def handle_case_commands(self, args):
    module_name = get_module_name(args)

    if args.subcommand == 'add_bt':
      self.service.add_bt(args.case_name, module_name)
    elif args.subcommand == 'add_st':
      self.service.add_st(args.case_name, args.case_c_name, args.case_c_group, module_name)
    elif args.subcommand == 'exist':
      self.service.exist(args.case_name, module_name)
    elif args.subcommand == 'rename':
      self.service.rename(args.old_case_name, args.new_case_name, module_name)
    elif args.subcommand == 'list':
      self.service.list_cases(module_name)
    elif args.subcommand == 'report':
      self.service.report(module_name)
    elif args.subcommand == 'del':
      input_code = input("[VCM] Please enter authorization code to delete the case: ")
      if input_code != AUTH_CODE:
        self.logger.log("Invalid authorization code. Case deletion aborted.", level="ERROR")
        return
      self.service.delete(args.case_name, module_name, input_code)
    elif args.subcommand == 'update_flag_bt':
      self.service.update_flag_bt(args.case_name, args.support_bt, module_name)
    elif args.subcommand == 'update_flag_st':
      self.service.update_flag_st(args.case_name, args.support_st, module_name)
    elif args.subcommand == 'update_flag_st_info':
      self.service.update_flag_st_info(args.case_name, args.case_c_name, args.case_c_group, module_name)
    elif args.subcommand == 'update_flag_regr':
      self.service.update_flag_regr(args.case_name, args.support_regr, module_name)
    elif args.subcommand == 'update_flag_post':
      self.service.update_flag_post(args.case_name, args.support_post, module_name)
    elif args.subcommand == 'update_flag_ams':
      self.service.update_flag_ams(args.case_name, args.support_ams, module_name)
    else:
      print("[VCM] Unknown case command. Use 'case -h' for help.")