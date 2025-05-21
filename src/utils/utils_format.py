import matplotlib.pyplot as plt
from collections import defaultdict
from item.regr_list_item import RegrListItem
from item.regr_item import RegrItem
from item.task_item import TaskItem

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

def print_regr_case_status(regr_list_item: RegrListItem):
  """
  按regr分组统计并打印每个回归下case（task）的状态分布。
  包括：等待数、已完成检查数、检查通过/失败数，并以表格形式展示详细case状态。
  """
  regr: RegrItem
  t : TaskItem

  for regr in regr_list_item.get_regrs():
    # 统计waiting
    waiting = sum(1 for sim in getattr(regr, "sims", []) if getattr(sim, "status", "") == "TODO")
    tasks = regr.get_tasks()
    total = len(tasks)
    sim_ok = 0
    sim_todo = 0
    check_done = 0
    check_pass = 0
    check_fail = 0

    for t in tasks:
      for sim in t.get_sim_logs():
        status = getattr(sim, "status", "")
        sim_result = getattr(sim, "sim_result", "")
        if status == "OK":
          sim_ok += 1
        elif status == "TODO":
          sim_todo += 1
        elif status in ("CheckDone", "CheckFail"):
          check_done += 1
          if sim_result == "Pass":
            check_pass += 1
          elif sim_result == "Fail":
            check_fail += 1

    print(f"[VCM] regr_id: {regr.regr_id} - {regr.module_name} - {regr.case_list}")
    print(f"  Post: {regr.get_tasks()[0].status_post}, SDF: {regr.work_name}")
    print(f"  Total task : {total}")
    print(f"  Sim Pending: {waiting}")
    print(f"  Sim Finish : {sim_ok}")
    print(f"  Sim Checked: {check_done} (Pass: {check_pass}, Fail: {check_fail})")

    # 表格打印详细case状态
    headers = ["TaskID", "Finished", "TODO", "Checck Pass", "Check Fail", "Sim Total"]
    rows = []
    for t in tasks:
      logs = t.get_sim_logs()
      ok = sum(1 for sim in logs if getattr(sim, "status", "") == "OK")
      todo = sum(1 for sim in logs if getattr(sim, "status", "") == "TODO")
      pass_cnt = sum(1 for sim in logs if getattr(sim, "status", "") in ("CheckDone", "CheckFail") and getattr(sim, "sim_result", "") == "Pass")
      fail_cnt = sum(1 for sim in logs if getattr(sim, "status", "") in ("CheckDone", "CheckFail") and getattr(sim, "sim_result", "") == "Fail")
      rows.append([t.task_id, ok, todo, pass_cnt, fail_cnt, len(logs)])

    print_table(headers, rows)

    # show fail case name, and log_path
    for t in tasks:
      logs = t.get_sim_logs()
      for sim in logs:
        if getattr(sim, "sim_result", "") == "Fail":
          print(f"  [Fail] sim{sim.sim_id}: {sim.case_name} - {sim.case_seed} - {sim.sim_log}")