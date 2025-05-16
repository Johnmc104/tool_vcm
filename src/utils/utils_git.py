import os
import subprocess

def get_git_info():
  current_dir = os.getcwd()
  parent_dir = os.path.dirname(current_dir)
  gitmodules_path = None

  if os.path.exists(os.path.join(parent_dir, ".gitmodules")):
    gitmodules_path = parent_dir
    git_dv = (
      subprocess.check_output(["git", "rev-parse", "HEAD"])
      .strip()
      .decode("utf-8")
    )
  else:
    print("[VCM] Warning: No .gitmodules file found in the parent directories.")
    git_dv = None

  if gitmodules_path:
    rtl_path = os.path.join(gitmodules_path, "rtl")
    if os.path.exists(rtl_path):
      os.chdir(rtl_path)
      git_de = (
        subprocess.check_output(["git", "rev-parse", "HEAD"])
        .strip()
        .decode("utf-8")
      )
      os.chdir(gitmodules_path)
    else:
      print("[VCM] Warning: No 'rtl' folder found in the parent directory.")
      git_de = None
  else:
    print("[VCM] Warning: No .gitmodules file found in the parent directories.")
    git_de = None

  status_output = (
    subprocess.check_output(["git", "status", "--porcelain"])
    .strip()
    .decode("utf-8")
  )
  if status_output:
    print("[VCM] Warning: There are uncommitted changes in the repository:")
    print(status_output)

  return git_de, git_dv

def get_module_name_from_git():
  try:
    repo_path = (
      subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
      .strip()
      .decode("utf-8")
    )
    git_name = os.path.basename(repo_path)
    return git_name.upper()
  except subprocess.CalledProcessError:
    return None
    
def get_project_name_from_git():
  module_name = get_module_name_from_git()
  if module_name and (
    module_name.startswith("GP")
    or module_name.startswith("GF")
    or module_name.startswith("M")
  ):
    parts = module_name.split("_")
    if len(parts) > 1:
      return parts[0].upper()
  return None

def get_project_and_module_name():
  module_name = get_module_name_from_git()

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
  else:
    print("[VCM] Warning: Unable to determine project or module name from git.")
    return None, None
  
def get_project_name(args):
  if hasattr(args, "project_name") and args.project_name:
    return args.project_name
  
  project_name = get_project_name_from_git()
  
  if not project_name:
    print("[VCM] Error: Unable to determine project name from Git repository.")
    return None
  return project_name

def get_module_name(args):
  if hasattr(args, "module_name") and args.module_name:
    return args.module_name
  
  module_name = get_module_name_from_git()
  
  if not module_name:
    print("[VCM] Error: Unable to determine module name from Git repository.")
    return None
  return module_name