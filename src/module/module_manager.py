from base_manager import BaseManager
from project.project_manager import ProjectManager

class ModuleManager(BaseManager):
  def add_module(self, module_name: str, project_id: int, created_by: str):
    """
    添加一个新模块。

    参数:
      module_name (str): 模块名称。
      project_id (int): 所属项目的ID。
      created_by (str): 创建者用户名。

    返回:
      None
    """
    self.cursor.execute(
      '''
      INSERT INTO modules (module_name, project_id, created_by)
      VALUES (?, ?, ?)
      ''', (module_name, project_id, created_by)
    )
    return
  
  def exist_module(self, module_name: str):
    """
    检查模块是否存在。

    参数:
      module_name (str): 模块名称。

    返回:
      bool: 如果模块存在返回 True，否则返回 False。
    """
    self.cursor.execute(
      '''
      SELECT module_id FROM modules WHERE module_name = ?
      ''', (module_name,)
    )
    return self.cursor.fetchone() is not None

  def find_module_id_by_name(self, module_name: str):
    """
    根据模块名称查找模块ID。

    参数:
      module_name (str): 模块名称。

    返回:
      int or None: 模块ID，未找到返回 None。
    """
    self.cursor.execute(
      '''
      SELECT module_id FROM modules WHERE module_name = ?
      ''', (module_name,)
    )
    module_id = self.cursor.fetchone()
    return module_id[0] if module_id else None

  def find_module_name_by_id(self, module_id: int):
    """
    根据模块ID查找模块名称。

    参数:
      module_id (int): 模块ID。

    返回:
      str or None: 模块名称，未找到返回 None。
    """
    self.cursor.execute(
      '''
      SELECT module_name FROM modules WHERE module_id = ?
      ''', (module_id,)
    )
    module_name = self.cursor.fetchone()
    return module_name[0] if module_name else None

  def update_module_name(self, old_module_name: str, new_module_name: str):
    """
    更新模块名称。

    参数:
      old_module_name (str): 原模块名称。
      new_module_name (str): 新模块名称。

    返回:
      None
    """
    self.cursor.execute(
      '''
      UPDATE modules SET module_name = ? WHERE module_name = ?
      ''', (new_module_name, old_module_name)
    )

  def delete_module(self, module_name: str):
    """
    删除指定名称的模块。

    参数:
      module_name (str): 模块名称。

    返回:
      None
    """

    self.cursor.execute(
      '''
      DELETE FROM modules WHERE module_name = ?
      ''', (module_name,)
    )

  def get_modules_by_project(self, project_id: int):
    """
    获取指定项目下的所有模块。

    参数:
      project_id (int): 项目名称。

    返回:
      list: 模块信息的元组列表，未找到项目时返回空列表。
    """

    self.cursor.execute(
      '''
      SELECT * FROM modules WHERE project_id = ?
      ''', (project_id,)
    )
    return self.cursor.fetchall()
  
  def get_all_modules(self):
    """
    获取所有模块信息。

    返回:
      list: 所有模块的元组列表。
    """
    self.cursor.execute('SELECT * FROM modules')
    return self.cursor.fetchall()