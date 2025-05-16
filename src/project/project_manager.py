from base_manager import BaseManager

class ProjectManager(BaseManager):
  def add_project(self, project_name: str, created_by: str):
    """
    添加一个新项目。

    功能:
      使用给定的名称和创建者添加新项目，项目名称统一存为大写以保证一致性。

    参数:
      project_name (str): 项目名称。
      created_by (str): 创建者用户名。

    返回:
      None
    """
    self.cursor.execute(
      '''
      INSERT INTO projects (project_name, created_by)
      VALUES (?, ?)
      ''', (project_name.upper(), created_by)
    )

  def find_project_id_by_name(self, project_name: str):
    """
    根据项目名称查找项目（不区分大小写）。

    参数:
      project_name (str): 项目名称。

    返回:
      int or None: 如果找到则返回 project_id，否则返回 None。
    """
    self.cursor.execute(
      '''
      SELECT project_id FROM projects WHERE project_name = ?
      ''', (project_name,)
    )
    project_id = self.cursor.fetchone()
    return project_id[0] if project_id else None
  
  def find_project_name_by_id(self, project_id: int):
    """
    根据项目 ID 查找项目名称。

    参数:
      project_id (int): 项目 ID。

    返回:
      str or None: 如果找到则返回项目名称，否则返回 None。
    """
    self.cursor.execute(
      '''
      SELECT project_name FROM projects WHERE project_id = ?
      ''', (project_id,)
    )
    project_name = self.cursor.fetchone()
    return project_name[0] if project_name else None

  def fetch_projects(self):
    """
    获取所有项目。

    返回:
      list: 包含所有项目的元组列表。
    """
    self.cursor.execute('SELECT * FROM projects')
    return self.cursor.fetchall()

  def update_project_name(self, old_name: str, new_name: str):
    """
    更新项目名称。

    参数:
      old_name (str): 原项目名称。
      new_name (str): 新项目名称。

    返回:
      None
    """
    self.cursor.execute(
      '''
      SELECT project_id FROM projects WHERE project_name = ?
      ''', (old_name.upper(),)
    )
    project_id = self.cursor.fetchone()
    if project_id:
      self.cursor.execute(
        '''
        UPDATE projects SET project_name = ? WHERE project_id = ?
        ''', (new_name.upper(), project_id[0])
      )
    else:
      print(f"未找到名称为 '{old_name}' 的项目。")

  def delete_project(self, project_name: str):
    """
    根据名称删除项目。

    参数:
      project_name (str): 项目名称。

    返回:
      None
    """
    self.cursor.execute(
      '''
      DELETE FROM projects WHERE project_name = ?
      ''', (project_name.upper(),)
    )

  def exist_project(self, project_name: str):
    """
    检查项目是否存在（通过名称）。

    参数:
      project_name (str): 项目名称。

    返回:
      bool: 存在返回 True，否则返回 False。
    """
    self.cursor.execute(
      '''
      SELECT 1 FROM projects WHERE project_name = ?
      ''', (project_name.upper(),)
    )
    return self.cursor.fetchone() is not None

  def get_all_project_names(self):
    """
    获取所有项目名称的列表。

    返回:
      list: 所有项目名称的列表。
    """
    self.cursor.execute('SELECT project_name FROM projects')
    return [row[0] for row in self.cursor.fetchall()]

  def get_project_by_id(self, project_id: int):
    """
    通过 project_id 获取项目详情。

    参数:
      project_id (int): 项目 ID。

    返回:
      tuple or None: 项目详情元组，未找到返回 None。
    """
    self.cursor.execute(
      'SELECT * FROM projects WHERE project_id = ?', (project_id,)
    )
    return self.cursor.fetchone()

  def get_project_details(self, project_name: str):
    """
    通过项目名称获取项目详情。

    参数:
      project_name (str): 项目名称。

    返回:
      tuple or None: 项目详情元组，未找到返回 None。
    """
    self.cursor.execute(
      '''
      SELECT * FROM projects WHERE project_name = ?
      ''', (project_name.upper(),)
    )
    return self.cursor.fetchone()

  def get_project_modules(self, project_name: str):
    """
    获取指定项目下的所有模块。

    参数:
      project_name (str): 项目名称。

    返回:
      list: 模块详情的元组列表。
    """
    self.cursor.execute(
      '''
      SELECT m.* FROM modules m
      JOIN projects p ON m.project_id = p.project_id
      WHERE p.project_name = ?
      ''', (project_name.upper(),)
    )
    return self.cursor.fetchall()

  def get_project_cases(self, project_name: str):
    """
    获取指定项目下的所有用例（通过 module_case_view 视图）。

    参数:
      project_name (str): 项目名称。

    返回:
      list: 用例详情的元组列表。
    """
    self.cursor.execute(
      '''
      SELECT * FROM module_case_view WHERE project_name = ?
      ''', (project_name.upper(),)
    )
    return self.cursor.fetchall()

  def count_projects(self):
    """
    统计项目总数。

    返回:
      int: 项目总数。
    """
    self.cursor.execute('SELECT COUNT(*) FROM projects')
    return self.cursor.fetchone()[0]