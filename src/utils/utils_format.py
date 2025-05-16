import matplotlib.pyplot as plt
from collections import defaultdict

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
