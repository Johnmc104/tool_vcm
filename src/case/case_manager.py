from project.project_manager import ProjectManager
from module.module_manager import ModuleManager
import re
import datetime

class CaseManager:
  def __init__(self, cursor):
    """
    初始化 CaseManager 实例。

    参数:
        cursor: 数据库游标对象，用于执行 SQL 操作。
    """
    self.cursor = cursor
    self.project_manager = ProjectManager(cursor)
    self.module_manager = ModuleManager(cursor)

  def add_case_basic(self, case_name: str, module_id: int, created_by: str) -> None:
    """
    添加基础用例信息。

    参数:
        case_name (str): 用例名称。
        module_id (int): 模块ID。
        created_by (str): 创建者。
    """

    self.cursor.execute(
      '''
      INSERT INTO case_info (case_name, case_c_name, case_c_group, module_id, support_bt, support_st, support_regr, support_post, support_ams, created_by)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      (case_name, '', '', module_id, False, False, False, False, False, created_by)
    )

  def add_case_bt(self, case_name: str, module_id: int, support_regr: bool, created_by: str) -> None:
    """
    添加BT类型用例信息。

    参数:
        case_name (str): 用例名称。
        module_id (int): 模块ID。
        support_regr (bool): 是否支持回归。
        created_by (str): 创建者。
    """

    self.cursor.execute(
      '''
      INSERT INTO case_info (case_name, case_c_name, case_c_group, module_id, support_bt, support_st, support_regr, support_post, support_ams, created_by)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      (case_name, '', '', module_id, True, False, support_regr, False, False, created_by)
    )

  def add_case_st(
    self,
    case_name: str,
    case_c_name: str,
    case_c_group: str,
    module_id: int,
    support_regr: bool,
    support_post: bool,
    support_ams: bool,
    created_by: str
  ) -> None:
    """
    添加ST类型用例信息。

    参数:
        case_name (str): 用例名称。
        case_c_name (str): 用例中文名。
        case_c_group (str): 用例分组。
        module_id (int): 模块ID。
        support_regr (bool): 是否支持回归。
        support_post (bool): 是否支持post。
        support_ams (bool): 是否支持ams。
        created_by (str): 创建者。
    """

    self.cursor.execute(
      '''
      INSERT INTO case_info (case_name, case_c_name, case_c_group, module_id, support_bt, support_st, support_regr, support_post, support_ams, created_by)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''',
      (case_name, case_c_name, case_c_group, module_id, False, True, support_regr, support_post, support_ams, created_by)
    )

  def find_cases_by_name(self, case_name: str) -> list:
    """
    根据用例名称查找所有相关用例。

    参数:
        case_name (str): 用例名称。

    返回:
        list: 包含(case_id, module_id)的元组列表。
    """
    self.cursor.execute('SELECT case_id, module_id FROM case_info WHERE case_name = ?', (case_name,))
    return self.cursor.fetchall()

  def find_case_id_by_module_id(self, case_name: str, module_id: int) :
    """
    根据用例名称和模块ID查找用例ID。

    参数:
        case_name (str): 用例名称。
        module_id (int): 模块ID。

    返回:
        int or None: 用例ID，若不存在则返回None。
    """
    self.cursor.execute('SELECT case_id FROM case_info WHERE case_name = ? AND module_id = ?', (case_name, module_id))
    case_id = self.cursor.fetchone()
    return case_id[0] if case_id else None

  def update_case_st(self, case_id: int, case_c_name: str = None, case_c_group: str = None) -> None:
    """
    更新用例为ST类型，并修改中文名和分组。

    参数:
        case_id (int): 用例ID。
        case_c_name (str): 用例中文名。
        case_c_group (str): 用例分组。
    """
    self.cursor.execute(
      '''
      UPDATE case_info
      SET support_st = ?, case_c_name = ?, case_c_group = ?
      WHERE case_id = ?
      ''',
      (True, case_c_name, case_c_group, case_id)
    )

  def update_flag_bt(self, case_id: int, support_bt: bool) -> None:
    """
    更新用例是否支持BT。

    参数:
        case_id (int): 用例ID。
        support_bt (bool): 是否支持BT。
    """
    self.cursor.execute('UPDATE case_info SET support_bt = ? WHERE case_id = ?', (support_bt, case_id))

  def update_flag_st(self, case_id: int, support_st: bool) -> None:
    """
    只更新用例是否支持ST。

    参数:
        case_id (int): 用例ID。
        support_st (bool): 是否支持ST。
    """
    self.cursor.execute(
      'UPDATE case_info SET support_st = ? WHERE case_id = ?',
      (support_st, case_id)
    )

  def update_flag_st_info(self, case_id: int, case_c_name: str, case_c_group: str) -> None:
    """
    只更新用例的中文名和分组。

    参数:
        case_id (int): 用例ID。
        case_c_name (str): 用例中文名。
        case_c_group (str): 用例分组。
    """
    self.cursor.execute(
      '''
      UPDATE case_info
      SET case_c_name = ?, case_c_group = ?
      WHERE case_id = ?
      ''',
      (case_c_name, case_c_group, case_id)
    )

  def get_st_info(self, case_id: int) :
    """
    获取用例的中文名和分组。

    参数:
        case_id (int): 用例ID。

    返回:
        tuple: (case_c_name, case_c_group)，均为str。
    """
    self.cursor.execute('SELECT case_c_name, case_c_group FROM case_info WHERE case_id = ?', (case_id,))
    result = self.cursor.fetchone()
    return result[0], result[1] if result else (None, None)

  def update_flag_regr(self, case_id: int, support_regr: bool) -> None:
    """
    更新用例是否支持回归。

    参数:
        case_id (int): 用例ID。
        support_regr (bool): 是否支持回归。
    """
    self.cursor.execute('UPDATE case_info SET support_regr = ? WHERE case_id = ?', (support_regr, case_id))

  def update_flag_post(self, case_id: int, support_post: bool) -> None:
    """
    更新用例是否支持POST。

    参数:
        case_id (int): 用例ID。
        support_post (bool): 是否支持POST。
    """
    self.cursor.execute('UPDATE case_info SET support_post = ? WHERE case_id = ?', (support_post, case_id))

  def update_flag_ams(self, case_id: int, support_ams: bool) -> None:
    """
    更新用例是否支持AMS。

    参数:
        case_id (int): 用例ID。
        support_ams (bool): 是否支持AMS。
    """
    self.cursor.execute('UPDATE case_info SET support_ams = ? WHERE case_id = ?', (support_ams, case_id))

  

  def exist_case(self, case_name: str, module_id: int):
    """
    判断指定模块下用例是否存在。

    参数:
        case_name (str): 用例名称。
        module_id (int): 模块id。

    返回:
        bool: 存在返回True, 否则False。
    """
    return self.find_case_id_by_module_id(case_name, module_id) is not None

  def update_case_name(self, old_case_name: str, new_case_name: str, module_name: str) -> None:
    """
    更新指定模块下的用例名称。

    参数:
        old_case_name (str): 原用例名称。
        new_case_name (str): 新用例名称。
        module_name (str): 模块名称。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if module_id is None:
      print(f"[VCM] Module '{module_name}' does not exist.")
      return
    self.cursor.execute(
      '''
      UPDATE case_info
      SET case_name = ?
      WHERE case_name = ? AND module_id = ?
      ''',
      (new_case_name, old_case_name, module_id)
    )

  def delete_case(self, case_name: str, module_name: str) -> None:
    """
    删除指定模块下的用例。

    参数:
        case_name (str): 用例名称。
        module_name (str): 模块名称。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if module_id is None:
      print(f"[VCM] Module '{module_name}' does not exist.")
      return
    self.cursor.execute('DELETE FROM case_info WHERE case_name = ? AND module_id = ?', (case_name, module_id))

  def list_cases(self, module_name: str) -> list:
    """
    列出指定模块下的所有用例。

    参数:
        module_name (str): 模块名称。

    返回:
        list: 用例信息列表。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if module_id is None:
      print(f"[VCM] Module '{module_name}' does not exist.")
      return []
    self.cursor.execute('SELECT * FROM case_info WHERE module_id = ?', (module_id,))
    return self.cursor.fetchall()