import os
import json
import datetime
from constants import get_current_user, get_current_dir, get_current_time, get_current_host, NODE_MAP
from utils.utils_git import get_module_name, get_git_info
from utils.utils_env import get_comp_corner, determine_regr_type, check_comp_result, get_node_info
from task.task_manager import TaskManager
from module.module_manager import ModuleManager
from item.task_item import TaskItem
from utils.utils_lib import rm_vcm_fail_file, add_vcm_fail_file
from item.regr_item import RegrItem
from item.task_item import TaskItem

class TaskService:
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.logger = logger
    self.manager = TaskManager(cursor)
    self.module_manager = ModuleManager(cursor)

  def add_task(self, args, comp_file="comp.log", json_file="vcm_task_info.json"):
    status_log = rm_vcm_fail_file("vcm.comp.fail")
    
    json_file_path = os.path.join(os.getcwd(), json_file)
    current_dir_name = os.path.basename(os.getcwd())
    current_user = get_current_user()
    current_host = get_current_host()

    # 检查当前目录
    if not (current_dir_name.startswith("sim_pre") or current_dir_name.startswith("sim_post") or current_dir_name.startswith("regr")):
      self.logger.log("Current directory must be sim_pre, sim_post, or regr.", level="ERROR")
      return

    # 用 TaskItem 读取或初始化
    task_item = TaskItem.load_from_file(json_file_path)

    if current_dir_name.startswith("regr"):
      task_item.status_regr = "True"
    else:
      task_item.status_regr = "False"

    # comp.log 路径
    comp_log_path = os.path.join(os.getcwd(), comp_file)
    if not os.path.exists(comp_log_path):
      self.logger.log(f"comp.log file not found at '{comp_log_path}'.", level="ERROR")
      return
    else:
      comp_result = check_comp_result(self.logger, comp_log_path)
      if comp_result is False:
        task_item.status_check = "False"
        add_vcm_fail_file(status_log, "Error: comp.log file does not contain valid compilation result.")
        return
      else:
        task_item.status_check = "True"

    # 跳过未变更
    comp_log_mtime_str = datetime.datetime.fromtimestamp(
      os.path.getmtime(comp_log_path)
    ).strftime('%Y-%m-%d %H:%M:%S')

    comp_log_changed = (
      task_item.comp_log_time != comp_log_mtime_str or
      task_item.current_user != current_user or
      task_item.current_host != current_host
    )

    if (
      not comp_log_changed and
      task_item.task_id is not None
    ):
      self.logger.log("comp.log has not changed and task already added by this user/host. Skipping.", level="INFO")
      return

    updated = False

    # 初始化任务
    module_name = get_module_name(args)
    module_id = self.module_manager.find_module_id_by_name(module_name)
    git_de, git_dv = get_git_info()
    task_id = self.manager.add_task_base(module_id, current_user, git_de, git_dv, current_host)
    task_item.git_de = git_de
    task_item.git_dv = git_dv
    task_item.task_id = task_id
    task_item.clear_sim_logs()
    self.logger.log("sim_logs cleared due to new compilation.", level="INFO")
    updated = True
    
    # 添加 post
    if task_item.status_post == "None":
      corner_name = get_comp_corner(self.logger, comp_log_path)
      if corner_name is not None:
        self.manager.update_task_post(task_id, corner_name)
        task_item.status_post = corner_name
      else:
        task_item.status_post = "False"
      updated = True

    # 更新时间戳和用户信息
    task_item.comp_log_time = comp_log_mtime_str
    task_item.current_user = current_user
    task_item.current_host = current_host

    # 只在有更新时写入文件
    if updated or True:
      task_item.save_to_file(json_file_path)
      self.logger.log(f"Task info updated and saved to '{json_file_path}'.", level="INFO")
    return

  def update_task_regr_id(self, task_id, regr_id) -> None:
    """
    更新任务的回归 ID。
    ...
    """

    if task_id is None and regr_id is None:
      #current_dir must be regr
      current_dir_name = os.path.basename(os.getcwd())
      if not current_dir_name.startswith("slurm"):
        self.logger.log("Current directory must be slurm.", level="ERROR")
        return
      
      regr_item = RegrItem.load_from_json()
      regr_id = regr_item.regr_id
      user_name = regr_item.current_user

      regr_item.clear_tasks()

      #part_name, part_mode, node_name, work_name = self.manager.get_regr_node_info(regr_id)
      part_name = regr_item.part_name
      part_mode = regr_item.part_mode
      node_name = regr_item.node_name
      work_name = regr_item.work_name

      nodes_name = get_node_info(part_name, part_mode, node_name)

      for node_item in nodes_name:
        node_dir = "/" + node_item["host_name"]

        vcm_task_info_path = os.path.join(
          node_dir, "work", user_name, work_name, "regr", "vcm_task_info.json"
        )
        if not os.path.exists(vcm_task_info_path):
          self.logger.log(f"{vcm_task_info_path} file not found.", level="ERROR")
          return
        
        task_item = TaskItem.load_from_file(vcm_task_info_path)
        task_id = task_item.task_id
        
        if task_id is None:
          self.logger.log(f"task_id not found in vcm_task_info.json.", level="ERROR")
          return
        
        self.manager.update_task_regr_id(task_id, True, regr_id)
        self.logger.log(f"Task ID '{task_id}' updated with regr ID '{regr_id}'.", level="INFO")

        regr_item.tasks = [t for t in regr_item.tasks if t.task_id != task_id]
        regr_item.tasks.append(task_item)
        
    else:
      self.manager.update_task_regr_id(task_id, False, regr_id)

    regr_item.save_to_json()

  def list_tasks(self, count=None):
    return self.manager.list_tasks(limit=count)
  
  def append_sim_log_to_task_info(self, task_info , sim_log_entry , file_vcm_task: str) -> None:
    """
    向 task_info 中追加仿真日志，并写回文件。
    ...
    """
    if "sim_logs" not in task_info or not isinstance(task_info["sim_logs"], list):
      task_info["sim_logs"] = []
    task_info["sim_logs"].append(sim_log_entry)
    with open(file_vcm_task, "w") as f:
      json.dump(task_info, f, indent=2)

  
