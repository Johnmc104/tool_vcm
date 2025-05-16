import os
from constants import get_current_dir
from db_manager import init_database
import json
import matplotlib.pyplot as plt
from collections import defaultdict

def get_db_name(debug=False):
  if debug:
    db_dir = get_current_dir()
  else:
    vtool_home = os.getenv("VTOOL_HOME")
    if not vtool_home:
      raise EnvironmentError("Environment variable VTOOL_HOME is not set.")
  
    db_dir = os.path.join(vtool_home, "data")
  db_name = os.path.join(db_dir, "vcm.db")
  return db_dir, db_name

def create_db_file(cursor, db_name):
  init_database(cursor)
  os.chmod(db_name, 0o1777)
  db_dir = os.path.dirname(db_name)
  os.chmod(db_dir, 0o1777)
  print("[VCM] Database initialized.")

def fetch_with_headers(cursor, sql, params=()):
  """
  执行 SQL 查询并返回结果及表头。

  功能:
    执行给定的 SQL 查询，返回所有结果行和对应的列名。

  参数:
    cursor: 数据库游标对象。
    sql (str): 要执行的 SQL 查询语句。
    params (tuple): 查询参数，默认为空元组。

  返回:
    tuple: (rows, headers)
      rows (list): 查询结果的所有行。
      headers (list): 列名列表。
  """
  cursor.execute(sql, params)
  rows = cursor.fetchall()
  headers = [desc[0] for desc in cursor.description]
  return rows, headers

def generate_html_report_with_chart(sims, headers, filename='simulation_report.html'):
  daily_results = defaultdict(lambda: {'error_num': 0, 'timing_num': 0, 'count': 0})
  for sim in sims:
    day = sim[4].split()[0]  # 假设第5列是创建日期
    error_num = sim[7] if sim[7] is not None else 0  # 假设第8列是功能错误数量
    timing_num = sim[8] if sim[8] is not None else 0  # 假设第9列是时序错误数量
    daily_results[day]['error_num'] += error_num
    daily_results[day]['timing_num'] += timing_num
    daily_results[day]['count'] += 1

  days = sorted(daily_results.keys())
  error_rates = [(daily_results[day]['error_num'] + daily_results[day]['timing_num']) / daily_results[day]['count'] for day in days]
  error_rates_func = [daily_results[day]['error_num'] / daily_results[day]['count'] for day in days]
  error_rates_timing = [daily_results[day]['timing_num'] / daily_results[day]['count'] for day in days]

  plt.figure(figsize=(10, 6))
  plt.scatter(days, error_rates_func, color='blue', label='Functional Error Rates')
  plt.scatter(days, error_rates_timing, color='green', label='Timing Error Rates')
  plt.plot(days, error_rates, color='red', linestyle='--', label='Total Error Rates')
  plt.xlabel('Day')
  plt.ylabel('Error Rate')
  plt.title('Error Rate Trend Over Days')
  plt.legend()
  plt.grid(True)
  plt.savefig('error_trend.png')

  html_content = f'''
    <html>
    <head>
      <title>Simulation Report</title>
      <style>
      table {{
        border-collapse: collapse;
        width: 100%;
      }}
      th, td {{
        border: 1px solid black;
        padding: 8px;
        text-align: left;
      }}
      th {{
        position: sticky;
        top: 0;
        background-color: #f2f2f2;
      }}
      .pagination {{
        display: flex;
        justify-content: center;
        margin-top: 20px;
      }}
      .pagination button {{
        margin: 0 5px;
        padding: 10px 20px;
        cursor: pointer;
      }}
      </style>
      <script>
      let currentPage = 1;
      let recordsPerPage = 5;

      function changePage(page) {{
        const table = document.getElementById('simTable');
        const rows = table.getElementsByTagName('tr');
        const totalPages = Math.ceil((rows.length - 1) / recordsPerPage);

        if (page < 1) page = 1;
        if (page > totalPages) page = totalPages;

        for (let i = 1; i < rows.length; i++) {{
          rows[i].style.display = 'none';
        }}

        for (let i = (page - 1) * recordsPerPage + 1; i <= page * recordsPerPage && i < rows.length; i++) {{
          rows[i].style.display = '';
        }}

        document.getElementById('page').innerText = 'Page ' + page + ' of ' + totalPages;
        currentPage = page;
      }}

      function prevPage() {{
        changePage(currentPage - 1);
      }}

      function nextPage() {{
        changePage(currentPage + 1);
      }}

      function setRecordsPerPage(num) {{
        recordsPerPage = num;
        changePage(1);
      }}

      function filterByDateRange() {{
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const table = document.getElementById('simTable');
        const rows = table.getElementsByTagName('tr');

        for (let i = 1; i < rows.length; i++) {{
          const date = rows[i].getElementsByTagName('td')[4].innerText.split(' ')[0];
          if (date >= startDate && date <= endDate) {{
            rows[i].style.display = '';
          }} else {{
            rows[i].style.display = 'none';
          }}
        }}
      }}

      window.onload = function() {{
        changePage(1);
      }}
      </script>
    </head>
    <body>
      <h1>Simulation Report</h1>
      <h2>Error Rate Trend Over Days</h2>
      <img src="error_trend.png" alt="Error Trend">
      <div>
        <label for="startDate">Start Date:</label>
        <input type="date" id="startDate" name="startDate">
        <label for="endDate">End Date:</label>
        <input type="date" id="endDate" name="endDate">
        <button onclick="filterByDateRange()">Filter</button>
      </div>
      <div class="pagination">
        <button onclick="prevPage()">Previous</button>
        <button onclick="nextPage()">Next</button>
        <span id="page"></span>
        <select onchange="setRecordsPerPage(this.value)">
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="50">50</option>
        </select>
      </div>
      <table id="simTable">
        <tr>
  '''
  for header in headers:
    html_content += f'<th>{header}</th>'
  html_content += '</tr>'

  for sim in sims:
    html_content += '<tr>'
    for item in sim:
      html_content += f'<td>{item}</td>'
    html_content += '</tr>'

  html_content += '''
      </table>
    </body>
    </html>
  '''

  with open(filename, 'w') as f:
    f.write(html_content)


def print_table(headers, rows):
  """
  通用表格打印函数。
  headers: 列名列表
  rows:    数据行，每行为字符串列表
  """
  if not rows:
    print("[VCM] No data found.")
    return

  # 计算每列最大宽度
  all_rows = [headers] + rows
  col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]

  # 打印分隔线
  sum_widths = sum(col_widths) + 3 * (len(headers) - 1)
  line = "-" * sum_widths
  print(line)

  # 打印标题
  header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
  print(header_line)
  print(line)

  # 打印内容
  for row in rows:
    print(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))))
  print(line)

def save_regr_info_to_json(regr_info: dict, json_path: str = "vcm_regr_info.json") -> None:
  """
  保存regr_id及其信息到json文件。

  参数:
    regr_id: 回归ID
    regr_info: 字典，包含回归信息
    json_path: json文件路径
  """
    
  json_file_path = os.path.join(get_current_dir(), json_path)

  with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(regr_info, f, ensure_ascii=False, indent=2)

def read_regr_info_from_json(json_path: str = "vcm_regr_info.json") -> dict:
  """
  从json文件中读取regr_id及其信息。

  参数:
    json_path: json文件路径
      
  返回:
    data: 字典，包含回归信息
  """
  json_file_path = os.path.join(get_current_dir(), json_path)
  if os.path.exists(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as f:
      try:
        data = json.load(f)
        return data
      except Exception:
        return {}
  else:
    return {}
    
def rm_vcm_fail_file(file_name: str = "vcm.fail"):
  """
  删除vcm.fail文件。
  """
  status_log = file_name
  if os.path.exists(status_log):
    os.remove(status_log)
    print(f"[VCM] Warning: File '{status_log}' removed.")
  return status_log

def add_vcm_fail_file(file_name: str = "vcm.fail", msg: str = "Error: please check case_list and fix problems."):
  """
  添加vcm.fail文件。
  """

  with open(file_name, "w") as f:
    f.write(msg)
    