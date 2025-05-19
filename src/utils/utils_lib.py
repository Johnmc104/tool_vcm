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

  if not os.path.exists(db_dir):
    print(f"[VCM] Error: Directory '{db_dir}' does not exist. Creating it.")

  db_name = os.path.join(db_dir, "vcm.db")
  return db_dir, db_name

def create_db_file(cursor, db_name):
  init_database(cursor)
  try:
    os.chmod(db_name, 0o1777)
    db_dir = os.path.dirname(db_name)
    os.chmod(db_dir, 0o1777)
    print("[VCM] Database initialized.")
  except Exception as e:
    print(f"[VCM] Warning: Failed to set permissions: {e}")

def save_regr_info_to_json(regr_info: dict, json_path: str = "vcm_regr_info.json") -> None:
  """
  将回归信息字典保存为指定路径的 JSON 文件。

  参数:
    regr_info (dict): 包含回归信息的字典。
    json_path (str): JSON 文件保存路径，默认为 "vcm_regr_info.json"。

  返回值:
    None
  """
    
  if not isinstance(regr_info, dict):
    raise ValueError("regr_info must be a dictionary.")
  json_file_path = os.path.join(get_current_dir(), json_path)
  try:
    with open(json_file_path, "w", encoding="utf-8") as f:
      json.dump(regr_info, f, ensure_ascii=False, indent=2)
  except Exception as e:
    print(f"[VCM] Error saving regression info: {e}")

def read_regr_info_from_json(json_path: str = "vcm_regr_info.json") -> dict:
  """
  读取指定路径的 JSON 文件，并返回回归信息字典。

  参数:
    json_path (str): JSON 文件路径，默认为 "vcm_regr_info.json"。

  返回值:
    dict: 包含回归信息的字典，若读取失败则返回空字典。
  """
  json_file_path = os.path.join(get_current_dir(), json_path)
  if os.path.exists(json_file_path):
    try:
      with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, dict):
          print(f"[VCM] Warning: Data in {json_file_path} is not a dictionary.")
          return {}
        return data
    except Exception as e:
      print(f"[VCM] Error reading regression info: {e}")
      return {}
  else:
    print(f"[VCM] Info: {json_file_path} does not exist.")
    return {}
    
def rm_vcm_fail_file(file_name: str = "vcm.fail"):
  """
  删除指定名称的 vcm.fail 文件。

  参数:
    file_name (str): 要删除的文件名，默认为 "vcm.fail"。

  返回值:
    str: 被删除或尝试删除的文件名。
  """
  status_log = file_name
  if os.path.exists(status_log):
    try:
      os.remove(status_log)
      print(f"[VCM] Warning: File '{status_log}' removed.")
    except Exception as e:
      print(f"[VCM] Error removing file '{status_log}': {e}")
  else:
    print(f"[VCM] Info: File '{status_log}' does not exist.")
  return status_log

def add_vcm_fail_file(file_name: str = "vcm.fail", msg: str = "Error: please check case_list and fix problems."):
  """
  创建指定名称的 vcm.fail 文件，并写入错误提示信息。

  参数:
    file_name (str): 要创建的文件名，默认为 "vcm.fail"。
    msg (str): 写入文件的错误信息，默认为 "Error: please check case_list and fix problems."。

  返回值:
    None
  """

  try:
    with open(file_name, "w") as f:
      f.write(msg)
    print(f"[VCM] Fail file '{file_name}' created.")
  except Exception as e:
    print(f"[VCM] Error creating fail file '{file_name}': {e}")