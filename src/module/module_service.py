from module.module_manager import ModuleManager
from project.project_manager import ProjectManager
from utils.utils_git import get_module_name
from constants import *

class ModuleService:
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.logger = logger
    self.manager = ModuleManager(cursor)
    self.project_manager = ProjectManager(cursor)
    

  def add_module(self, project_name: str, module_name: str):
    creator = get_current_user()

    project_id = self.project_manager.find_project_id_by_name(project_name)

    if not module_name or not project_id:
      self.logger.log(f"Module name or project ID is missing.", level="ERROR")
      return False, module_name, project_name
    if self.manager.exist_module(module_name):
      self.logger.log(f"Module '{module_name}' already exists.", level="INFO")
      return False, False, project_name
    
    self.manager.add_module(module_name, project_id, creator)
    self.logger.log(f"Module '{module_name}' added to project '{project_name}'.", level="INFO")
    return True, module_name, project_name

  def rename_module(self, old_name, new_name):
    if old_name == new_name:
      return False
    self.manager.update_module_name(old_name, new_name)
    return True

  def module_exists(self, module_name):
    exists = self.manager.find_module_id_by_name(module_name)
    return exists

  def list_modules(self, project_name):
    project_id = self.project_manager.find_project_id_by_name(project_name)
    if not project_id:
      print(f"Project '{project_name}' not found.")
      return []
    modules = self.manager.get_modules_by_project(project_id)
    return modules

  def delete_module(self):
    module_name = get_module_name()
    if not module_name:
      print("Module name is required.")

    if not self.manager.exist_module(module_name):
      print(f"Module '{module_name}' does not exist.")
    
    self.manager.delete_module(module_name)
    return 