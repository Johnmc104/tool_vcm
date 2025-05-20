
from utils.utils_format import fetch_with_headers

class SimManager:
  def __init__(self, cursor):
    """
    初始化 SimManager 实例

    参数:
        cursor: 数据库游标对象，用于执行 SQL 操作
    """
    self.cursor = cursor

  def add_sim_basic_regr(self, case_id, job_id, case_seed, created_by):
    """
    向 sim_info 表添加回归仿真记录

    参数:
        case_id (int): 仿真用例ID
        job_id (int): 作业ID
        case_seed (int): 用例种子
        created_by (str): 创建人

    返回:
        int: 新插入记录的ID
    """
    self.cursor.execute(
      '''INSERT INTO sim_info (case_id, job_id, case_seed, created_by)
         VALUES (?, ?, ?, ?)''',
      (case_id, job_id, case_seed, created_by)
    )
    return self.cursor.lastrowid

  def add_sim_basic_single(self, case_id, case_seed, task_id, created_by):
    """
    向 sim_info 表添加单次仿真记录（非回归）

    参数:
        case_id (int): 仿真用例ID
        case_seed (int): 用例种子
        task_id (int): 关联任务ID
        created_by (str): 创建人

    返回:
        int: 新插入记录的ID
    """
    self.cursor.execute(
      '''INSERT INTO sim_info (case_id, case_seed, task_id, job_id, created_by)
         VALUES (?, ?, ?, ?, ?)''',
      (case_id, case_seed, task_id, 0, created_by)
    )
    return self.cursor.lastrowid

  def update_sim_dir(self, sim_id, sim_dir):
    """
    更新指定仿真ID的仿真目录

    参数:
        sim_id (int): 仿真ID
        sim_dir (str): 仿真目录路径
    """
    self.cursor.execute(
      '''UPDATE sim_info SET sim_dir = ? WHERE sim_id = ?''',
      (sim_dir, sim_id)
    )

  def update_sim_create_at(self, sim_id, create_at):
    """
    更新指定仿真ID的创建时间

    参数:
        sim_id (int): 仿真ID
        create_at (str): 创建时间
    """
    self.cursor.execute(
      '''UPDATE sim_info SET created_at = ? WHERE sim_id = ?''',
      (create_at, sim_id)
    )

  def update_sim_node_dir(self, sim_id, job_id, job_dir):
    """
    更新指定仿真ID的节点名、作业ID和仿真目录

    参数:
        sim_id (int): 仿真ID
        job_id (int): 作业ID
        job_dir (str): 仿真目录路径
    """
    self.cursor.execute(
      '''UPDATE sim_info SET job_dir = ?, job_id = ?, WHERE sim_id = ?''',
      (job_dir, job_id, sim_id)
    )

  def update_sim_time_pass(self, sim_id, sim_time, error_num, timing_num, is_pass):
    """
    更新指定仿真ID的仿真时间、错误数和时序数

    参数:
        sim_id (int): 仿真ID
        sim_time (int): 仿真时间
        error_num (int): 错误数
        timing_num (int): 时序数
    """
    self.cursor.execute(
      '''UPDATE sim_info SET sim_time = ?, error_num = ?, timing_num = ?, is_check = ?, is_pass = ? WHERE sim_id = ?''',
      (sim_time, error_num, timing_num, True, is_pass, sim_id)
    )

  def update_sim_task_id(self, sim_id, task_id):
    """
    更新指定仿真ID的任务ID

    参数:
        sim_id (int): 仿真ID
        task_id (int): 任务ID
    """
    self.cursor.execute(
      '''UPDATE sim_info SET task_id = ? WHERE sim_id = ?''',
      (task_id, sim_id)
    )

  def fetch_sims(self):
    """
    获取 sim_info 表中所有仿真记录

    返回:
        list: 所有仿真记录的列表
    """
    self.cursor.execute('SELECT * FROM sim_info')
    return self.cursor.fetchall()

  def query_sim_info(self, case_name=None, project_name=None, module_name=None, user=None):
    """
    根据用例名、项目名、模块名或用户查询仿真信息
    """
    query = '''
      SELECT sim_info.* FROM sim_info
      JOIN case_info ON sim_info.case_id = case_info.case_id
      JOIN modules ON case_info.module_id = modules.module_id
      JOIN projects ON modules.project_id = projects.project_id
      WHERE 1=1
    '''
    params = []
    if project_name:
        query += ' AND projects.project_name = ?'
        params.append(project_name)
    elif module_name:
        query += ' AND modules.module_name = ?'
        params.append(module_name)
    elif user:
        query += ' AND sim_info.created_by = ?'
        params.append(user)
    else:
        raise ValueError("必须提供 project_name、module_name 或 user 其中之一。")
    if case_name:
        query += ' AND case_info.case_name = ?'
        params.append(case_name)
    return fetch_with_headers(self.cursor, query, tuple(params))

