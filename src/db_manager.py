"""
数据库连接与初始化
"""
import sqlite3
from constants import VCM_DB_DEFAULT
from contextlib import contextmanager
#import pymysql
from constants import MYSQL_EN, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, VCM_DB_DEFAULT

@contextmanager
def db_connection(db_name=VCM_DB_DEFAULT):

  if MYSQL_EN:
    #conn = pymysql.connect(
    #  host=MYSQL_HOST,
    #  user=MYSQL_USER,
    #  password=MYSQL_PASSWORD,
    #  database=MYSQL_DB,
    #  charset='utf8mb4'
    #)
    pass
  else:
    conn = sqlite3.connect(db_name)
    try:
      yield conn
    finally:
      conn.commit()
      conn.close()

# 初始化数据库并创建表
def init_database(cursor):
  # 创建 projects 表
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
      project_id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_name TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT (DATETIME('now', '+8 hours')),
      created_by TEXT
    )
  ''')

  # 创建 modules 表
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS modules (
      module_id INTEGER PRIMARY KEY AUTOINCREMENT,
      module_name TEXT NOT NULL,
      project_id INTEGER,
      created_at TIMESTAMP DEFAULT (DATETIME('now', '+8 hours')),
      created_by TEXT,
      FOREIGN KEY (project_id) REFERENCES projects(project_id)
    )
  ''')

  # 创建 case_info 表
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS case_info (
      case_id INTEGER PRIMARY KEY AUTOINCREMENT,
      module_id INTEGER,
      created_at TIMESTAMP DEFAULT (DATETIME('now', '+8 hours')),
      created_by TEXT,
      case_name TEXT NOT NULL,
      case_c_name TEXT DEFAULT NULL,
      case_c_group TEXT DEFAULT NULL,
      support_st BOOLEAN DEFAULT FALSE,
      support_bt BOOLEAN DEFAULT FALSE,
      support_regr BOOLEAN DEFAULT FALSE,
      support_post BOOLEAN DEFAULT FALSE,
      support_ams BOOLEAN DEFAULT FALSE,
      FOREIGN KEY (module_id) REFERENCES modules(module_id)
    )
  ''')

  # 创建 regrs 表
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS regr_info (
      regr_id INTEGER PRIMARY KEY AUTOINCREMENT,
      module_id INTEGER,
      created_at TIMESTAMP DEFAULT (DATETIME('now', '+8 hours')),
      created_by TEXT,
      regr_base TEXT,
      regr_type TEXT,
      part_name TEXT,
      part_mode TEXT check(part_mode in ('multi', 'single')),
      node_name TEXT,
      work_name TEXT,
      work_url TEXT,
      case_list TEXT
    )
  ''')
  #regr_type TEXT check(regr_type in ('eman', 'slurm', 'lsf')),

  # 创建 tasks 表
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
      task_id INTEGER PRIMARY KEY AUTOINCREMENT,
      module_id INTEGER,
      created_at TIMESTAMP DEFAULT (DATETIME('now', '+8 hours')),
      created_by TEXT,
      git_de TEXT,
      git_dv TEXT,
      is_regr BOOLEAN DEFAULT FALSE,
      regr_id INTEGER DEFAULT NULL,
      node_name TEXT,
      is_post BOOLEAN DEFAULT FALSE,
      corner_name TEXT,
      FOREIGN KEY (module_id) REFERENCES modules(module_id),
      FOREIGN KEY (regr_id) REFERENCES regrs(regr_id)
    )
  ''')

  # 创建 sim_info 表
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS sim_info (
      sim_id INTEGER PRIMARY KEY AUTOINCREMENT,
      case_id INTEGER,
      task_id INTEGER,
      created_at TIMESTAMP DEFAULT (DATETIME('now', '+8 hours')),
      created_by TEXT,
      case_seed TEXT,
      job_id INTEGER DEFAULT 0,
      job_dir TEXT,
      is_check BOOLEAN,
      sim_time INTEGER,
      error_num INTEGER,
      timing_num INTEGER,
      is_pass BOOLEAN,
      FOREIGN KEY (task_id) REFERENCES tasks(task_id),
      FOREIGN KEY (case_id) REFERENCES case_info(case_id)
    )
  ''')

  # IDX
  cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_name ON projects(project_name);')
  cursor.execute('CREATE INDEX IF NOT EXISTS idx_modules_project_id ON modules(project_id);')

  #View
  cursor.execute('''
  CREATE VIEW IF NOT EXISTS project_modules_view AS
  SELECT 
    projects.project_id,
    projects.project_name,
    modules.module_id,
    modules.module_name
  FROM 
    projects
  LEFT JOIN 
    modules ON projects.project_id = modules.project_id;
  ''')
  # SELECT * FROM project_modules_view WHERE project_name = ?

  cursor.execute('''
  CREATE VIEW IF NOT EXISTS module_case_view AS
  SELECT 
    modules.module_id,
    modules.module_name,
    projects.project_name,
    case_info.case_id,
    case_info.case_name,
    case_info.case_c_name,
    case_info.case_c_group,
    case_info.created_at,
    case_info.created_by,
    case_info.support_bt,
    case_info.support_st,
    case_info.support_regr,
    case_info.support_post,
    case_info.support_ams
  FROM 
    modules
  LEFT JOIN 
    case_info ON modules.module_id = case_info.module_id
  LEFT JOIN 
    projects ON modules.project_id = projects.project_id;
  ''')
  #  SELECT * FROM module_case_view WHERE project_name = ?

  cursor.execute('''
  CREATE VIEW IF NOT EXISTS module_task_view AS
  SELECT 
      modules.module_id,
      modules.module_name,
      tasks.task_id,
      tasks.git_de,
      tasks.git_dv,
      tasks.corner_name,
      tasks.is_regr
  FROM 
      modules
  LEFT JOIN 
      tasks ON modules.module_id = tasks.module_id;
  ''')
  #查询某个模块下的所有任务
  # SELECT * FROM module_task_view WHERE module_name = ?
  #查询所有的 regression 任务
  # SELECT * FROM module_task_view WHERE is_regr = 1
  #查询某模块中包含特定角点的任务
  # SELECT * FROM module_task_view WHERE module_name = ? AND corner_name = ?

  cursor.execute('''
  CREATE VIEW IF NOT EXISTS task_sim_view AS
  SELECT 
    modules.module_name,
    tasks.task_id,
    tasks.git_de,
    tasks.git_dv,
    case_info.case_name,
    sim_info.sim_id,
    sim_info.sim_time,
    sim_info.error_num,
    sim_info.timing_num,
    sim_info.job_id
  FROM 
    tasks
  LEFT JOIN 
    sim_info ON tasks.task_id = sim_info.task_id
  LEFT JOIN 
    case_info ON sim_info.case_id = case_info.case_id
  LEFT JOIN 
    modules ON case_info.module_id = modules.module_id
  ''')
  #查询某个任务的仿真信息
  # SELECT * FROM task_sim_view WHERE task_id = ?
  #查询仿真中有错误的任务
  # SELECT * FROM task_sim_view WHERE error_num > 0