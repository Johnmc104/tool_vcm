from project.project_manager import ProjectManager
from project.project_report import generate_project_report
from constants import AUTH_CODE, get_current_user

class ProjectService:
  """
  项目服务层，负责业务逻辑。
  """
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.manager = ProjectManager(cursor)
    self.logger = logger

  def add_project(self, project_name):
    if self.manager.exist_project(project_name):
      self.logger.log(f"Project '{project_name}' already exists.", level="INFO")
      return False
    creator = get_current_user()
    self.manager.add_project(project_name, creator)
    self.logger.log(f"Project '{project_name}' added by '{creator}'.", level="INFO")
    return True

  def exist_project(self, project_name):
    exists = self.manager.exist_project(project_name)
    msg = f"Project '{project_name}' exists." if exists else f"Project '{project_name}' does not exist."
    self.logger.log(msg, level="INFO")
    return exists

  def rename_project(self, old_name, new_name):
    if not self.manager.exist_project(old_name):
      self.logger.log(f"Project '{old_name}' does not exist.", level="INFO")
      return False
    self.manager.update_project_name(old_name, new_name)
    self.logger.log(f"Project '{old_name}' renamed to '{new_name}'.", level="INFO")
    return True

  def list_projects(self):
    projects = self.manager.fetch_projects()
    if not projects:
      self.logger.log("No projects found.", level="INFO")
      return False
    #self.logger.log(f"Projects listed: {projects}", level="INFO")
    return True, projects

  def report_project(self, project_name):
    if not self.manager.exist_project(project_name):
      self.logger.log(f"Project '{project_name}' does not exist.", level="INFO")
      return False
    generate_project_report(self.cursor, project_name)
    self.logger.log(f"Project report generated for '{project_name}'.", level="INFO")
    return True

  def delete_project(self, project_name, input_code):
    if not self.manager.exist_project(project_name):
      self.logger.log(f"Project '{project_name}' does not exist.", level="INFO")
      return False
    if input_code != AUTH_CODE:
      self.logger.log("Invalid authorization code. Project deletion aborted.", level="INFO")
      return False
    self.manager.delete_project(project_name)
    self.logger.log(f"Project '{project_name}' has been deleted.", level="INFO")
    return True