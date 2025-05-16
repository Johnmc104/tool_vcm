import os
from constants import get_current_dir
from db_manager import init_database
import json
import matplotlib.pyplot as plt
from collections import defaultdict
from constants import check_vtool_home

def get_db_name(debug=False):
  if debug:
    db_dir = os.path.join(get_current_dir(), "data")
    print(f"[VCM] Debug mode: Using database directory: {db_dir}")
  else:
    vtool_home = check_vtool_home()
    db_dir = os.path.join(vtool_home, "data")

  db_name = os.path.join(db_dir, "vcm.db")
  return db_dir, db_name

def create_db_file(cursor, db_name):
  init_database(cursor)
  os.chmod(db_name, 0o1777)
  db_dir = os.path.dirname(db_name)
  os.chmod(db_dir, 0o1777)
  print("[VCM] Database initialized.")


def save_regr_info_to_json(regr_info: dict, json_path: str = "vcm_regr_info.json") -> None:
  """
  保存regr_id及其信息到json文件。

  参数:
    regr_id: 回归ID
    regr_info: 字典，包含回归信息
    json_path: json文件路径
  """
    
  json_file_path = os.path.join(get_current_dir(), json_path)

  with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(regr_info, f, ensure_ascii=False, indent=2)

def read_regr_info_from_json(json_path: str = "vcm_regr_info.json") -> dict:
  """
  从json文件中读取regr_id及其信息。

  参数:
    json_path: json文件路径
      
  返回:
    data: 字典，包含回归信息
  """
  json_file_path = os.path.join(get_current_dir(), json_path)
  if os.path.exists(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as f:
      try:
        data = json.load(f)
        return data
      except Exception:
        return {}
  else:
    return {}
    
def rm_vcm_fail_file(file_name: str = "vcm.fail"):
  """
  删除vcm.fail文件。
  """
  status_log = file_name
  if os.path.exists(status_log):
    os.remove(status_log)
    print(f"[VCM] Warning: File '{status_log}' removed.")
  return status_log

def add_vcm_fail_file(file_name: str = "vcm.fail", msg: str = "Error: please check case_list and fix problems."):
  """
  添加vcm.fail文件。
  """

  with open(file_name, "w") as f:
    f.write(msg)
    