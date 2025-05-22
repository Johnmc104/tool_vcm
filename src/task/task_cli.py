from task.task_service import TaskService
from task.task_report import print_tasks_table
from task.task_manager import TaskManager

class TaskCLI:
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.logger = logger
    self.service = TaskService(cursor, logger)
    self.manager = TaskManager(cursor)

  def add_task_subcommands(subparsers):
    commands = {
      "add": {
        "help": "Add a new task. Provide creator's name and optional comp.log path.",
        "usage": "%(prog)s [comp_log_path]",
        "arguments": [
          ("comp_log_path", "Path to the comp.log file (optional)", {"nargs": "?"})
        ]
      },
      "add_only": {
        "help": "Add a new task. Provide creator's name and optional comp.log path, but do not add to db.",
        "usage": "%(prog)s [comp_log_path]",
        "arguments": [
          ("comp_log_path", "Path to the comp.log file (optional)", {"nargs": "?"})
        ]
      },
      "add_db": {
        "help": "Add task to db",
        "usage": "%(prog)s ",
        "arguments": [
        ]
      },
      "add_db_regr": {
        "help": "Add task to db with regression",
        "usage": "%(prog)s [part_name] [part_mode] [node_name] [work_name]",
        "arguments": [
          ("part_name", "Part name (e.g., 'digit' or 'edas')"),
          ("part_mode", "Part mode (e.g., 'single' or 'multi')"),
          ("node_name", "Node name (e.g., 'digit01', 'eda')"),
          ("work_name", "Work name (e.g., 'regr')")
        ]
      },
      "update_regr_id": {
        "help": "Update the regression ID for a task.",
        "usage": "%(prog)s [task_id] [regr_id]",
        "arguments": [
          ("task_id", "Task ID", {"nargs": "?"}),
          ("regr_id", "Regression ID", {"nargs": "?"})
        ]
      },
      "list": {
        "help": "list all tasks.",
        "usage": "%(prog)s [-n COUNT]",
        "arguments": [
          ("-n", "Number of tasks to show (default: all)", {"dest": "count", "type": int, "default": None})
        ]
      }
    }

    for cmd, config in commands.items():
      parser = subparsers.add_parser(cmd, help=config["help"], usage=config["usage"])
      for arg in config["arguments"]:
        if len(arg) == 2:
          name, help_text = arg
          parser.add_argument(name, help=help_text)
        elif len(arg) == 3:
          name, help_text, kwargs = arg
          parser.add_argument(name, help=help_text, **kwargs)
        else:
          raise ValueError(f"Invalid argument format for command '{cmd}': {arg}")

  def handle_task_commands(self, args):
    if args.subcommand == 'add':
      self.service.add_task(args)
    elif args.subcommand == 'add_only':
      self.service.add_task_only(args)
    elif args.subcommand == 'add_db':
      self.service.commit_task_to_db(args)
    elif args.subcommand == 'update_regr_id':
      if (args.task_id is None) != (args.regr_id is None):
        self.logger.error("--task_id and --regr_id must both be provided or both omitted.", level="ERROR")
        return
      
      if args.task_id is None and args.regr_id is None:
        self.service.update_task_regr_id(args.task_id, args.regr_id)
      else:
        self.manager.update_task_regr_id(args.task_id, False, args.regr_id)
    elif args.subcommand == 'list':
      tasks = self.service.list_tasks(count=args.count)
      print_tasks_table(self.cursor, tasks)
    else:
      print("[VCM] Unknown task command. Use 'task -h' for help.")