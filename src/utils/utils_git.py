import os
import subprocess

def get_git_info():
  """
  获取Git仓库的关键信息，包括dv和de的commit hash，并检测仓库是否有未提交的更改。

  Returns:
    tuple: (git_de, git_dv)
      git_de (str or None): rtl目录下的commit hash（如存在），否则为None。
      git_dv (str or None): 父目录下的commit hash（如存在），否则为None。
  """
  current_dir = os.getcwd()
  parent_dir = os.path.dirname(current_dir)
  gitmodules_path = None
  git_dv = None
  git_de = None

  if os.path.exists(os.path.join(parent_dir, ".gitmodules")):
    gitmodules_path = parent_dir
    try:
      git_dv = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=gitmodules_path)
        .strip()
        .decode("utf-8")
      )
    except subprocess.CalledProcessError:
      print("[VCM] Error: Failed to get git commit hash for dv.")
      git_dv = None
  else:
    print("[VCM] Warning: No .gitmodules file found in the parent directories.")

  if gitmodules_path:
    rtl_path = os.path.join(gitmodules_path, "rtl")
    if os.path.exists(rtl_path):
      try:
        git_de = (
          subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=rtl_path)
          .strip()
          .decode("utf-8")
        )
      except subprocess.CalledProcessError:
        print("[VCM] Error: Failed to get git commit hash for de.")
        git_de = None
    else:
      print("[VCM] Warning: No 'rtl' folder found in the parent directory.")
  else:
    print("[VCM] Warning: No .gitmodules file found in the parent directories.")

  try:
    status_output = (
      subprocess.check_output(["git", "status", "--porcelain"], cwd=gitmodules_path or current_dir)
      .strip()
      .decode("utf-8")
    )
    if status_output:
      print("[VCM] Warning: There are uncommitted changes in the repository:")
      print(status_output)
  except subprocess.CalledProcessError as e:
    print(f"[VCM] Error: Failed to get git status. {e}")

  return git_de, git_dv

def get_module_name_from_git():
  """
  获取当前Git仓库的模块名（即顶层目录名，全部大写）。

  Returns:
    str or None: 模块名（大写），获取失败时返回None。
  """
  try:
    repo_path = (
      subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
      .strip()
      .decode("utf-8")
    )
    git_name = os.path.basename(repo_path)
    return git_name.upper()
  except subprocess.CalledProcessError as e:
    print(f"[VCM] Error: Unable to get module name from git. {e}")
    return None
    
def get_project_name_from_git():
  """
  根据模块名推断项目名（以GP、GF或M开头，取下划线前缀）。

  Returns:
    str or None: 项目名（大写），获取失败时返回None。
  """
  module_name = get_module_name_from_git()
  if module_name and (
    module_name.startswith("GP")
    or module_name.startswith("GF")
    or module_name.startswith("M")
  ):
    parts = module_name.split("_")
    if parts:
      return parts[0].upper()
  print("[VCM] Warning: Module name does not match expected project prefix.")
  return None

def get_project_and_module_name_from_git():
  """
  同时获取项目名和模块名。

  Returns:
    tuple: (project_name, module_name)
      project_name (str or None): 项目名（大写），获取失败时为None。
      module_name (str or None): 模块名（大写），获取失败时为None。
  """
  module_name = get_module_name_from_git()
  project_name = None

  if module_name and (
    module_name.startswith("GP")
    or module_name.startswith("GF")
    or module_name.startswith("M")
  ):
    parts = module_name.split("_")
    if len(parts) > 1:
      project_name = parts[0].upper()

  if module_name and project_name:
    return project_name, module_name
  print("[VCM] Warning: Unable to determine project or module name from git.")
  return None, None
  
def get_project_name(args):
  """
  获取项目名，优先从参数args中获取，否则从Git仓库推断。

  Args:
    args (object): 具有project_name属性的参数对象。

  Returns:
    str or None: 项目名（大写），获取失败时返回None。
  """
  if hasattr(args, "project_name") and args.project_name:
    return args.project_name.upper()
  
  project_name = get_project_name_from_git()

  if not project_name:
    print("[VCM] Error: Unable to determine project name from Git repository.")
    return None
  return project_name

def get_module_name(args):
  """
  获取模块名，优先从参数args中获取，否则从Git仓库推断。

  Args:
    args (object): 具有module_name属性的参数对象。

  Returns:
    str or None: 模块名（大写），获取失败时返回None。
  """
  if hasattr(args, "module_name") and args.module_name:
    return args.module_name.upper()
  
  module_name = get_module_name_from_git()
  
  if not module_name:
    print("[VCM] Error: Unable to determine module name from Git repository.")
    return None
  return module_name
