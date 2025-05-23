from info.info_service import InfoService
from utils.utils_env import get_job_status_name
class InfoCLI:
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.logger = logger
    self.service = InfoService(cursor, logger)

  def add_info_subcommands(subparsers):
    """
    向 argparse 的 subparsers 添加模块相关的子命令。

    参数:
      subparsers: argparse 的 subparsers 对象。
    """

    commands = {
      "caselist": {
        "help": "get case list, check case is exist.",
        "usage": "%(prog)s <caselist_name> [module_name]",
        "arguments": [
          ("caselist_name", "Name of the caselist"),
          ("module_name", "Name of the module", {"nargs": "?"})
        ]
      },
      "emclist": {
        "help": "get emc list, get emc info.",
        "usage": "%(prog)s <emc_name> [module_name]",
        "arguments": [
          ("emc_name", "Name of the emc"),
          ("module_name", "Name of the module", {"nargs": "?"})
        ]
      },
      "createlist": {
        "help": "create case list from emclist.",
        "usage": "%(prog)s <emc_name> [module_name]",
        "arguments": [
          ("emc_name", "Name of the emc"),
          ("module_name", "Name of the module", {"nargs": "?"})
        ]
      },
      "checkcomp":{
        "help": "get comp.fail and check.",
        "usage": "%(prog)s <part_name> <part_mode> <node_name> <work_name> [module_name]",
        "arguments": [
          ("part_name", "slurm partition name"),
          ("part_mode", "slurm partition mode"),
          ("node_name", "slurm node name"),
          ("work_name", "slurm work name"),
          ("module_name", "Name of the module", {"nargs": "?"})
        ]
      },
      "jobstatus":{
        "help": "get job status.",
        "usage": "%(prog)s <job_id>",
        "arguments": [
          ("job_id", "slurm job id")
        ]
      },
      "regrlist":{
        "help": "get regression list, print all regression info.",
        "usage": "%(prog)s [module_name]",
        "arguments": [
          ("module_name", "Module name", {"nargs": "?"})
        ]
      },
      "find_sw":{
        "help": "find software info.",
        "usage": "%(prog)s <case_name> [module_name]",
        "arguments": [
          ("case_name", "Name of the case"),
          ("module_name", "Name of the module", {"nargs": "?"})
        ]
      }
    }

    for cmd, config in commands.items():
      parser = subparsers.add_parser(cmd, help=config["help"], usage=config["usage"])
      for arg in config["arguments"]:
        arg_name, arg_help, *arg_options = arg
        parser.add_argument(arg_name, help=arg_help, **(arg_options[0] if arg_options else {}))

  def handle_info_commands(self, args):
    """
    处理信息相关的命令行参数。

    参数:
      args: 命令行参数对象。
    """
    if args.subcommand == "caselist":
      self.service._handle_caselist(args)
    elif args.subcommand == "emclist":
      self.service._handle_emclist(args)
    elif args.subcommand == "createlist":
      self.service._handle_createlist(args)
    elif args.subcommand == "checkcomp":
      self.service._handle_checkcomp(args)
    elif args.subcommand == "jobstatus":
      job_id = args.job_id
      status, node_name = get_job_status_name(job_id)
      if status is None:
        print(f"[VCM] Error: Job ID '{job_id}' not found.")
      else:
        print(f"[VCM] Job ID: {job_id}, Status: '{status}', Node: '{node_name}'")
    elif args.subcommand == "regrlist":
      self.service._handle_regrlist(args)
    elif args.subcommand == "find_sw":
      self.service._handle_find_sw(args)
    else:
      print("[VCM] Unknown command. Use '-h' for help.")