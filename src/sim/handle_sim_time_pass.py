
import os
from sim.sim_manager import SimManager
from item.regr_item import RegrItem
from item.task_item import TaskItem
from item.sim_item import SimItem
from utils.utils_env import check_sim_single_function_result, check_sim_single_timing_result
import subprocess
from utils.utils_log import Logger
from typing import List

def process_single_sim_info(logger:Logger, args, sim_manager, sim_info, post_flag):
  sim_id = sim_info.get("sim_id")
  job_id = sim_info.get("job_id")
  sim_log = sim_info.get("sim_log")

  tim_result = 0
  fun_result = check_sim_single_function_result(sim_log)
  if post_flag:
    tim_result = check_sim_single_timing_result(sim_log)

  if fun_result is None or tim_result is None:
    logger.log(f"sim_id '{sim_id}' has no function or timing result, skipping.", level="WARNING")
    sim_info["status"] = "CheckFail"
    sim_info["check_result"] = "Unknown"
    return sim_info

  #logger.log(f"sim_id '{sim_id}' function result: {fun_result}, timing result: {tim_result}", level="INFO")

  total_result = fun_result + tim_result


  if job_id == 0 or job_id is None:
    if args.sim_time is None:
      logger.log(f"sim_time is not provided for sim_id '{sim_id}'.", level="ERROR")
      sim_time = 0
    else:
      sim_time = args.sim_time
  else:
    sim_time = get_job_elapsed_time(job_id)

  try:
    sim_time = int(sim_time)
  except (TypeError, ValueError):
    sim_time = 0

  if sim_time is None:
    logger.log(f"sim_id '{sim_id}' has no elapsed time, skipping.", level="WARNING")
    sim_info["status"] = "CheckFail"
    sim_info["check_result"] = "Unknown"
    return sim_info
  
  # 检查结果
  if total_result == 0:
    sim_info["status"] = "CheckDone"
    sim_info["check_result"] = "Pass"
    sim_manager.update_sim_time_pass(sim_id, sim_time, fun_result, tim_result, True)
    logger.log(f"sim_id '{sim_id}' function result: {fun_result}, timing result: {tim_result}, check pass", level="INFO")
  else:
    sim_info["status"] = "CheckDone"
    sim_info["check_result"] = "Fail"
    sim_manager.update_sim_time_pass(sim_id, sim_time, fun_result, tim_result, False)
    logger.log(f"sim_id '{sim_id}' has error in function or timing result. at {sim_log}", level="ERROR")
  return sim_info

def get_job_elapsed_time(job_id):
  # 调用 sacct 命令
  result = subprocess.run(
    ['sacct', '-j', str(job_id), '--format=Elapsed', '--noheader'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True  # 替换 text=True
  )

  # 获取输出并处理，只取第一行
  elapsed_time = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ''
  
  # 将时间转换为秒
  if elapsed_time:
    # 处理不同格式的时间
    parts = elapsed_time.split(':')
    if len(parts) == 3:  # HH:MM:SS
      hours, minutes, seconds = map(int, parts)
      total_seconds = hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:  # MM:SS
      minutes, seconds = map(int, parts)
      total_seconds = minutes * 60 + seconds
    elif len(parts) == 1:  # SS
      total_seconds = int(parts[0])
    else:
      total_seconds = 0
    
    return total_seconds
  else:
    return None  # 作业可能不存在或没有执行时间
  
def handle_sim_time_pass(cursor, logger:Logger, args):
  sim_manager = SimManager(cursor)

  task_items : List[TaskItem]
  sim_items: List[SimItem]

  if os.path.basename(os.getcwd()) != "slurm":
    logger.log("Current directory must be 'slurm'.", level="ERROR")
    return

  regr_item = RegrItem.load_from_file()
  task_items = regr_item.get_tasks()
  if not task_items or not isinstance(task_items, list):
    logger.log("No task_item data found in regr_item.", level="ERROR")
    return

  task_item : TaskItem
  for task_item in task_items:
    sim_items = task_item.get_sims()
    if sim_items is None:
      logger.log("No sim_items found in a task_item.", level="ERROR")
      continue
  
    status_post = getattr(task_item, "status_post", "False")
    post_flag = False if status_post in ("False", "None") else True
  
    sim_item : SimItem
    for sim_item in sim_items:
      # sim_item 是 SimItem 实例
      sim_info = sim_item.to_dict()
      sim_info = process_single_sim_info(logger, args, sim_manager, sim_info, post_flag)
      # 直接更新 sim_item 的属性
      sim_item.status = sim_info.get("status", sim_item.status)
      sim_item.check_result = sim_info.get("check_result", sim_item.check_result)
      sim_item.sim_log = sim_info.get("sim_log", sim_item.sim_log)

  # 保存整个 regr_item
  regr_item.save_to_file()