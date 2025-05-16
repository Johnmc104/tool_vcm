from module.module_manager import ModuleManager
from base_manager import BaseManager

class RegrManager(BaseManager):
  def __init__(self, cursor):
    """
    初始化 RegrManager 实例。

    参数:
      cursor: 数据库游标对象，用于执行 SQL 操作。
    """
    self.cursor = cursor
    self.module_manager = ModuleManager(cursor)

  def add_regr(self, module_id: int, created_by: str, regr_base: str, regr_type: str) -> None:
    """
    添加回归记录。

    参数:
      module_id (int): 模块ID。
      created_by (str): 创建者。
      regr_base (str): 回归基线。
      regr_type (str): 回归类型。
    """
    self.cursor.execute(
      '''
      INSERT INTO regr_info (
        module_id, created_by, regr_base, regr_type
      ) VALUES (?, ?, ?, ?)
      ''',
      (module_id, created_by, regr_base, regr_type)
    )
    return self.cursor.lastrowid
  
  def update_slurm_info(self, regr_id: int, part_name: str, part_mode: str,
                        node_name: str, work_name: str, work_url: str,
                        case_list: str) -> None:
    """
    更新回归记录的 SLURM 信息。

    参数:
      regr_id (int): 回归ID。
      part_name (str): 分区名称。
      part_mode (str): 分区模式('multi'或'single')。
      node_name (str): 节点名称。
      work_name (str): 项目名称。
      work_url (str): 项目URL。
      case_list (str): 用例列表（逗号分隔）。
    """
    self.cursor.execute(
      '''
      UPDATE regr_info SET
        part_name = ?, part_mode = ?, node_name = ?, work_name = ?,
        work_url = ?, case_list = ?
      WHERE regr_id = ?
      ''',
      (part_name, part_mode, node_name, work_name, work_url, case_list, regr_id)
    )

  def find_regr_by_id(self, regr_id: int):
    """
    根据回归ID查找回归记录。

    参数:
      regr_id (int): 回归ID。

    返回:
      dict: 回归记录，若不存在则返回None。
    """
    self.cursor.execute('SELECT * FROM regr_info WHERE regr_id = ?', (regr_id,))
    row = self.cursor.fetchone()
    if row:
      columns = [desc[0] for desc in self.cursor.description]
      return dict(zip(columns, row))
    return None

  def list_regrs_by_module(self, module_id: int) -> list:
    """
    列出指定模块下的所有回归记录。

    参数:
      module_id (int): 模块名称。

    返回:
      list: 回归记录列表。
    """
    self.cursor.execute('SELECT * FROM regr_info WHERE module_id = ?', (module_id,))
    return self.cursor.fetchall()

  def delete_regr(self, regr_id: int) -> None:
    """
    删除指定回归记录。

    参数:
      regr_id (int): 回归ID。
    """
    self.cursor.execute('DELETE FROM regr_info WHERE regr_id = ?', (regr_id,))

  def exist_regr_by_module_id(self, regr_id: int, module_id: int):
    """
    判断回归记录是否存在。

    参数:
      regr_id (int): 回归ID。
      module_id (int): 模块ID。

    返回:
      bool: 存在返回True，否则False。
    """
    self.cursor.execute('SELECT 1 FROM regr_info WHERE regr_id = ? AND module_id = ?', (regr_id, module_id))
    
    return self.cursor.fetchone() is not None
  
  def exist_regr(self, regr_id: int):
    """
    判断回归记录是否存在。

    参数:
      regr_id (int): 回归ID。

    返回:
      bool: 存在返回True，否则False。
    """
    self.cursor.execute('SELECT 1 FROM regr_info WHERE regr_id = ?', (regr_id,))
    
    return self.cursor.fetchone() is not None