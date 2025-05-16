from case.case_manager import CaseManager
from module.module_manager import ModuleManager
from constants import AUTH_CODE, get_current_user
from case.case_report import generate_case_report
from case.case_report import print_cases_table

class CaseService:
  def __init__(self, cursor, logger):
    """
    初始化 CaseService 实例。

    参数:
      cursor: 数据库游标对象，用于数据库操作。
      logger: 日志记录器对象，用于记录日志信息。
    """
    self.cursor = cursor
    self.logger = logger
    self.manager = CaseManager(cursor)
    self.module_manager = ModuleManager(cursor)

  def add_bt(self, case_name: str, module_name: str):
    """
    添加 BT 类型的用例。

    参数:
      case_name (str): 用例名称。
      module_name (str): 模块名称。

    返回:
      bool: 添加成功返回 True，已存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if self.manager.exist_case(case_name, module_id):
      self.logger.log(f"Case '{case_name}' already exists under module '{module_name}'.", level="WARNING")
      return False
    self.manager.add_case_bt(case_name, module_id, False, get_current_user())
    self.logger.log(f"BT case '{case_name}' added under module '{module_name}'.", level="INFO")
    return True

  def add_st(self, case_name: str, case_c_name: str, case_c_group: str, module_name: str):
    """
    添加 ST 类型的用例。

    参数:
      case_name (str): 用例名称。
      case_c_name (str): ST 用例中文名称。
      case_c_group (str): ST 用例分组。
      module_name (str): 模块名称。

    返回:
      bool: 添加成功返回 True，已存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if self.manager.exist_case(case_name, module_id):
      self.logger.log(f"Case '{case_name}' already exists under module '{module_name}'.", level="WARNING")
      return False
    self.manager.add_case_st(case_name, case_c_name, case_c_group, module_id, False, False, False, get_current_user())
    self.logger.log(f"ST case '{case_name}' added under module '{module_name}'.", level="INFO")
    return True

  def exist(self, case_name: str, module_name: str):
    """
    检查用例是否存在于指定模块下。

    参数:
      case_name (str): 用例名称。
      module_name (str): 模块名称。

    返回:
      bool: 存在返回 True，否则返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if self.manager.exist_case(case_name, module_id):
      self.logger.log(f"Case '{case_name}' exists under module '{module_name}'.", level="INFO")
      return True
    self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="INFO")
    return False

  def rename(self, old_case_name: str, new_case_name: str, module_name: str) -> None:
    """
    重命名指定模块下的用例。

    参数:
      old_case_name (str): 原用例名称。
      new_case_name (str): 新用例名称。
      module_name (str): 模块名称。
    """
    self.manager.update_case_name(old_case_name, new_case_name, module_name)
    self.logger.log(f"Case '{old_case_name}' renamed to '{new_case_name}' under module '{module_name}'.", level="INFO")

  def list_cases(self, module_name: str) -> None:
    """
    列出指定模块下的所有用例。

    参数:
      module_name (str): 模块名称。
    """
    cases = self.manager.list_cases(module_name)
    if cases:
      print_cases_table(self.cursor, cases)
    else:
      print(f"[VCM] No cases found under module '{module_name}'.")

  def report(self, module_name: str):
    """
    生成指定模块下用例的报告。

    参数:
      module_name (str): 模块名称。

    返回:
      str: 用例报告内容。
    """
    return generate_case_report(self.manager, module_name)

  def delete(self, case_name: str, module_name: str):
    """
    删除指定模块下的用例。

    参数:
      case_name (str): 用例名称。
      module_name (str): 模块名称。

    返回:
      bool: 删除成功返回 True，不存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if not self.manager.exist_case(case_name, module_id):
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return False
    self.manager.delete_case(case_name, module_name)
    self.logger.log(f"Case '{case_name}' has been deleted from module '{module_name}'.", level="INFO")
    return True

  def update_flag_bt(self, case_name: str, support_bt: bool, module_name: str):
    """
    更新 BT 标志。

    参数:
      case_name (str): 用例名称。
      support_bt (bool): 是否支持 BT。
      module_name (str): 模块名称。

    返回:
      bool: 更新成功返回 True，不存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    case_id = self.manager.find_case_id_by_module_id(case_name, module_id)
    if case_id is None:
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return False
    self.manager.update_flag_bt(case_id, support_bt)
    self.logger.log(f"support_bt for case '{case_name}' updated to '{support_bt}'.", level="INFO")
    return True

  def update_flag_st(self, case_name: str, support_st: bool, module_name: str):
    """
    更新 ST 标志。

    参数:
      case_name (str): 用例名称。
      support_st (bool): 是否支持 ST。
      module_name (str): 模块名称。

    返回:
      bool: 更新成功返回 True，不存在返回 False。
    """
    #check support_st
    #if support_st is not True and support_st is not False:
    #  self.logger.log(f"support_st must be True or False, but got {support_st}.", level="ERROR")
    #  return False

    module_id = self.module_manager.find_module_id_by_name(module_name)
    case_id = self.manager.find_case_id_by_module_id(case_name, module_id)
    if case_id is None:
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return False
    self.manager.update_flag_st(case_id, support_st)
    self.logger.log(f"support_st for case '{case_name}' updated to '{support_st}'.", level="INFO")

    if support_st == 'True':
      case_c_name, case_c_group = self.manager.get_st_info(case_id)
      if case_c_name == '' or case_c_group == '':
        self.logger.log(f"added st flag, but not add st info, please add it quickly ", level="WARNING")
        return True

    return True

  def update_flag_st_info(self, case_name: str, case_c_name: str, case_c_group: str, module_name: str):
    """
    更新 ST 用例的中文名称和分组信息。

    参数:
      case_name (str): 用例名称。
      case_c_name (str): ST 用例中文名称。
      case_c_group (str): ST 用例分组。
      module_name (str): 模块名称。

    返回:
      bool: 更新成功返回 True，不存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    case_id = self.manager.find_case_id_by_module_id(case_name, module_id)
    if case_id is None:
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return False
    self.manager.update_flag_st_info(case_id, case_c_name, case_c_group)
    self.logger.log(f"case_c_name and case_c_group for case '{case_name}' updated.", level="INFO")
    return True
  
  def get_st_info(self, case_name: str, module_name: str):
    """
    获取 ST 用例的中文名称和分组信息。

    参数:
      case_name (str): 用例名称。
      module_name (str): 模块名称。

    返回:
      tuple: (case_c_name, case_c_group)，若不存在则返回 (None, None)。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    case_id = self.manager.find_case_id_by_module_id(case_name, module_id)
    if case_id is None:
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return None, None
    
    case_c_name, case_c_group = self.manager.get_st_info(case_id)
    if case_c_name is None or case_c_group is None:
      self.logger.log(f"Case '{case_name}' does not have ST info.", level="WARNING")
      return None, None
    return case_c_name, case_c_group

  def update_flag_regr(self, case_name: str, support_regr: bool, module_name: str):
    """
    更新回归标志。

    参数:
      case_name (str): 用例名称。
      support_regr (bool): 是否支持回归。
      module_name (str): 模块名称。

    返回:
      bool: 更新成功返回 True，不存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    case_id = self.manager.find_case_id_by_module_id(case_name, module_id)
    if case_id is None:
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return False
    self.manager.update_flag_regr(case_id, support_regr)
    self.logger.log(f"support_regr for case '{case_name}' updated to '{support_regr}'.", level="INFO")
    return True

  def update_flag_post(self, case_name: str, support_post: bool, module_name: str):
    """
    更新 Post 标志。

    参数:
      case_name (str): 用例名称。
      support_post (bool): 是否支持 Post。
      module_name (str): 模块名称。

    返回:
      bool: 更新成功返回 True，不存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    case_id = self.manager.find_case_id_by_module_id(case_name, module_id)
    if case_id is None:
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return False
    self.manager.update_flag_post(case_id, support_post)
    self.logger.log(f"support_post for case '{case_name}' updated to '{support_post}'.", level="INFO")
    return True

  def update_flag_ams(self, case_name: str, support_ams: bool, module_name: str):
    """
    更新 AMS 标志。

    参数:
      case_name (str): 用例名称。
      support_ams (bool): 是否支持 AMS。
      module_name (str): 模块名称。

    返回:
      bool: 更新成功返回 True，不存在返回 False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    case_id = self.manager.find_case_id_by_module_id(case_name, module_id)
    if case_id is None:
      self.logger.log(f"Case '{case_name}' does not exist under module '{module_name}'.", level="WARNING")
      return False
    self.manager.update_flag_ams(case_id, support_ams)
    self.logger.log(f"support_ams for case '{case_name}' updated to '{support_ams}'.", level="INFO")
    return True
