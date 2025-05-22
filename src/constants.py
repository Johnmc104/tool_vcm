"""
全局常量定义
"""
import os
import subprocess
import datetime

def get_current_user():
  try:
    return os.getlogin()
  except Exception:
    return os.environ.get("USER", "unknown")

def get_current_host():
  try:
    return subprocess.check_output(['hostname']).strip().decode('utf-8')
  except Exception:
    return "unknown"
  
def get_current_dir():
  try:
    return os.getcwd()
  except Exception:
    return "unknown"  
  
def get_current_time():
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_real_time(db_time, utc: int = 8):
  utc_dt = datetime.datetime.strptime(db_time, "%Y-%m-%d %H:%M:%S")
  bj_dt = utc_dt + datetime.timedelta(utc)
  return bj_dt.strftime("%Y-%m-%d %H:%M:%S")

def check_vtool_home():
  vtool_home = os.getenv("VTOOL_HOME")
  if not vtool_home:
    raise EnvironmentError("Environment variable VTOOL_HOME is not set.")
  return vtool_home

NODE_MAP = {
  "digit01": "home_d1",
  "digit02": "home_d2",
  "digit03": "home_d3",
  "digit04": "home_d4",
  "eda"  : "home",
  "eda4" : "home204",
  "eda5" : "home205",
  "eda6" : "home206",
  "eda7" : "home207",
  "eda8" : "home208",
  "eda9" : "home209",
  "eda10": "home210",
  "eda11": "home211",
  "eda12": "home212",
}

GEO_EN = False
AUTH_CODE = "hangzhou"
VCM_DB_DEFAULT = os.path.join(os.getcwd(), "vcm.db")
FILE_VCM_TASK = os.path.join(os.getcwd(), "vcm_task_info.json")
VCM_TASK_FILENAME = "vcm_task_info.json"
VCM_REGR_FILENAME = "vcm_regr_info.json"

REMOTE_EN = False
REMOTE_API_URL = "http://example.com/api"