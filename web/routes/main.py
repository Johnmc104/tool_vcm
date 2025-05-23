from flask import Blueprint, render_template
import sqlite3
import os

main_routes = Blueprint('main_routes', __name__)

def get_db_path():
    # 根据你的实际路径调整
    vtool_home = os.getenv("VTOOL_HOME", os.getcwd())
    db_dir = os.path.join(vtool_home, "data")
    db_path = os.path.join(db_dir, "vcm.db")
    return db_path

@main_routes.route('/projects')
def projects():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT project_id, project_name, created_at, created_by FROM projects")
    projects = cursor.fetchall()
    conn.close()
    return render_template('projects.html', projects=projects)

@main_routes.route('/modules')
def modules():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT module_id, module_name, project_id, created_at, created_by FROM modules")
    modules = cursor.fetchall()
    conn.close()
    return render_template('modules.html', modules=modules)

@main_routes.route('/cases')
def cases():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, module_id, case_name, case_c_name, case_c_group, created_at, created_by FROM case_info")
    cases = cursor.fetchall()
    conn.close()
    return render_template('cases.html', cases=cases)

@main_routes.route('/regrs')
def regrs():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT regr_id, module_id, regr_base, regr_type, part_name, part_mode, node_name, work_name, work_url, case_list, created_at, created_by FROM regr_info")
    regrs = cursor.fetchall()
    conn.close()
    return render_template('regrs.html', regrs=regrs)

@main_routes.route('/tasks')
def tasks():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, module_id, git_de, git_dv, is_regr, regr_id, node_name, is_post, corner_name, created_at, created_by FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return render_template('tasks.html', tasks=tasks)

@main_routes.route('/sims')
def sims():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT sim_id, case_id, task_id, case_seed, job_id, is_check, sim_time, error_num, timing_num, is_pass, created_at, created_by FROM sim_info")
    sims = cursor.fetchall()
    conn.close()
    return render_template('sims.html', sims=sims)