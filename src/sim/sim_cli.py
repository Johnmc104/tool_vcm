from sim.sim_service import SimService

class SimCLI:
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.logger = logger
    self.service = SimService(cursor, logger)

  @staticmethod
  def add_sim_subcommands(subparsers):
    commands = {
      "add_basic_single": {
        "help": "Add a new basic single simulation.",
        "usage": "%(prog)s [sim_log_path]",
        "arguments": [
          ("sim_log_path", "Path to the sim.log file (optional)", {"nargs": "?", "default": "sim.log"}),
          ("--sim_time", "Sim log time (optional)", {"type": str, "default": None})
        ]
      },
      "add_basic_regr": {
        "help": "Add a new basic regression simulation. ",
        "usage": "%(prog)s ",
        "arguments": [
        ]
      },
      "update_node_dir": {
        "help": "Update node name and simulation directory. after status check",
        "usage": "%(prog)s [sim_id] [node_name] [sim_dir]",
        "arguments": [
          ("sim_id", "ID of the simulation", {"nargs": "?"}),
          ("node_name", "Name of the node", {"nargs": "?"}),
          ("sim_dir", "Simulation directory", {"nargs": "?"})
        ]
      },
      "update_time_pass": {
        "help": "Update simulation time and pass status.",
        "usage": "%(prog)s ",
        "arguments": []
      },
      "list": {
        "help": "Fetch simulation records.",
        "usage": "%(prog)s <case_name> [--module_name MODULE_NAME] [--project_name PROJECT_NAME] [--user CREATED_BY]",
        "arguments": [
          ("case_name", "Name of the case", {"nargs": "?"}),
          ("--module_name", "Name of the module", {"nargs": "?"}),
          ("--project_name", "Name of the project", {"nargs": "?"}),
          ("--user", "Name of the creator", {"nargs": "?"}),
          ("--output", "Output format (console or html)", {"choices": ["console", "html"], "default": "console"})
        ]
      }
    }
    for cmd, config in commands.items():
      parser = subparsers.add_parser(cmd, help=config["help"], usage=config["usage"])
      for arg in config["arguments"]:
        if isinstance(arg, tuple):
          arg_name, arg_help, *arg_options = arg
          parser.add_argument(arg_name, help=arg_help, **(arg_options[0] if arg_options else {}))
        else:
          parser.add_argument(arg, help=config["arguments"][arg])

  def handle_sim_commands(self, args):
    if args.subcommand == 'add_basic_single':
      self.service.handle_add_basic_single(args)
    elif args.subcommand == 'add_basic_regr':
      self.service.handle_add_basic_regr(args)
    elif args.subcommand == 'update_node_dir':
      self.service.handle_update_node_dir(args)
    elif args.subcommand == 'update_time_pass':
      self.service.handle_sim_time_pass(args)
    elif args.subcommand == 'list':
      self.service.handle_list_sim_info(args)
    else:
      print("[VCM] Unknown sim command. Use 'sim -h' for help.")