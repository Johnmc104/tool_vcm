import json
import os
from typing import Optional, List, Dict, Any
from base_manager import BaseManager

class TaskManager(BaseManager):
  def add_task_base(self, module_id: int, created_by: str, git_de: str, git_dv: str, node_name:str) -> int:
    """
    向数据库中添加基础任务信息。
    ...
    """
    self.cursor.execute('''
      INSERT INTO tasks (module_id, created_by, git_de, git_dv, node_name)
      VALUES (?, ?, ?, ?, ?)
    ''', (module_id, created_by, git_de, git_dv, node_name))
    return self.cursor.lastrowid

  def update_task_post(self, task_id: int, corner_name: str) -> None:
    """
    更新任务为 post 类型，并设置 corner 名称。
    ...
    """
    self.cursor.execute('''
      UPDATE tasks
      SET is_post = ?, corner_name = ?
      WHERE task_id = ?
    ''', (True, corner_name, task_id))

  def update_task_regr(self, task_id: int, node_name:str) -> None:
    """
    更新任务为回归类型，并设置回归类型。
    ...
    """
    self.cursor.execute('''
      UPDATE tasks
      SET is_regr = ?, node_name = ?
      WHERE task_id = ?
    ''', (True, node_name, task_id))

  def update_task_regr_id(self, task_id: int, is_regr: bool,regr_id: int) -> None:
    """
    更新任务的回归 ID。
    ...
    """
    self.cursor.execute('''
      UPDATE tasks
      SET is_regr = ?, regr_id = ?
      WHERE task_id = ?
    ''', (is_regr, regr_id, task_id))

  def list_tasks(self, limit: Optional[int] = None) -> List[Any]:
    """
    获取任务列表，按 task_id 降序排列。
    ...
    """
    if limit is not None:
      self.cursor.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT ?', (limit,))
    else:
      self.cursor.execute('SELECT * FROM tasks ORDER BY task_id DESC')
    return self.cursor.fetchall()
  
  def get_regr_node_info(self, regr_id: int) -> Optional[Dict[str, Any]]:
    """
    获取回归节点信息。
      part_name, part_mode, node_name, work_name,
    """
    self.cursor.execute('''
      SELECT part_name, part_mode, node_name, work_name
      FROM regr_info
      WHERE regr_id = ?
    ''', (regr_id,))
    return self.cursor.fetchone()

  