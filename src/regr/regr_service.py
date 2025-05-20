from regr.regr_manager import RegrManager
from module.module_manager import ModuleManager
from constants import get_current_user
from item.regr_item import RegrItem
from item.regr_list_item import RegrListItem
from utils.utils_log import Logger

class RegrService:
  def __init__(self, cursor, logger: Logger):
    """
    初始化 RegrService 实例。

    参数:
      cursor: 数据库游标对象。
      logger: 日志记录器对象。
    """
    self.cursor = cursor
    self.logger = logger
    self.manager = RegrManager(cursor)
    self.module_manager = ModuleManager(cursor)

  def add_regr(self,regr_base: str,  regr_type: str, module_name: str, ) -> None:
    """
    添加回归记录。

    参数:
      module_name (str): 模块名称。
      其它参数同 regr_manager.add_regr。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    created_by = get_current_user()

    regr_list = RegrListItem.load_from_file()
    if not regr_list:
      print(f"[VCM] No regression list found.")
      return
    
    #create regr to db
    regr_id = self.manager.add_regr(module_id, created_by, regr_base, regr_type)
    if regr_id is None:
      print(f"[VCM] Failed to add regression record for module '{module_name}'.")
      return
    self.logger.log(f"Regr added for module '{module_name}'.", level="INFO")

    # 构造regr_info字典
    regr_item = RegrItem(regr_id, regr_type, module_name, module_id)

    regr_list.add_regr(regr_item)
    regr_list.save_to_file()

  def update_slurm_info(self, part_name: str, part_mode: str,
                        node_name: str, work_name: str, work_url: str,
                        case_list: str, module_name: str) -> None:
    """
    更新回归记录的 SLURM 信息。
    参数:
      part_name (str): 分区名称。
      part_mode (str): 分区模式('multi'或'single')。
      node_name (str): 节点名称。
      work_name (str): 项目名称。
      work_url (str): 项目URL。
      case_list (str): 用例列表（逗号分隔）。
      module_name (str): 模块名称。
    """
    regr_item: RegrItem

    regr_list = RegrListItem.load_from_file()
    if not regr_list:
      print(f"[VCM] No regression list found.")
      return

    regr_item = regr_list.get_regr_last()

    if not regr_item or regr_item.regr_id is None:
      print(f"[VCM] Regr ID not found in JSON file.")
      return
    regr_id = regr_item.regr_id
      
    # 检查回归记录是否存在
    if not self.manager.exist_regr(regr_id):
      self.logger.log(f"Regr '{regr_id}' does not exist at db.", level="WARNING")
      return
      
    self.manager.update_slurm_info(regr_id, part_name, part_mode, node_name,
                                  work_name, work_url, case_list)
    # 更新 regr_item 并保存
    regr_item.update_slurm_info(part_name, part_mode, node_name,
                                work_name, work_url, case_list)
    self.logger.log(f"SLURM info updated for regr '{regr_id}' under module '{module_name}'.", level="INFO")

    regr_list.update_regr(regr_item)

    # 保存更新后的回归记录
    regr_list.save_to_file()


  def exist(self, regr_id: int, module_name: str):
    """
    检查回归记录是否存在。

    参数:
      regr_id (int): 回归ID。
      module_name (str): 模块名称。

    返回:
      bool: 存在返回True，否则False。
    """
    
    exists = self.manager.exist_regr(regr_id)
    self.logger.log(f"Regr '{regr_id}' does not exist at db.", level="WARNING")
    return exists

  def find_by_id(self, regr_id: int):
    """
    根据回归ID查找回归记录。

    参数:
      regr_id (int): 回归ID。

    返回:
      dict: 回归记录，若不存在则返回None。
    """
    regr = self.manager.find_regr_by_id(regr_id)
    if regr:
      self.logger.log(f"Found regr '{regr_id}'.", level="INFO")
    else:
      self.logger.log(f"Regr '{regr_id}' not found.", level="WARNING")
    return regr

  def list_regrs(self, module_name: str) -> list:
    """
    列出指定模块下的所有回归记录。

    参数:
      module_name (str): 模块名称。

    返回:
      list: 回归记录列表。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    regrs = self.manager.list_regrs_by_module(module_id)
    if regrs:
      self.logger.log(f"Listed regrs for module '{module_name}'.", level="INFO")
    else:
      self.logger.log(f"No regrs found for module '{module_name}'.", level="INFO")
    return regrs

  def delete(self, regr_id: int, module_name: str):
    """
    删除指定回归记录。

    参数:
      regr_id (int): 回归ID。
      module_name (str): 模块名称。

    返回:
      bool: 删除成功返回True，不存在返回False。
    """
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if not self.manager.exist_regr(regr_id, module_id):
      self.logger.log(f"Regr '{regr_id}' does not exist at db.", level="WARNING")
      return False
    self.manager.delete_regr(regr_id)
    self.logger.log(f"Regr '{regr_id}' deleted from module '{module_name}'.", level="INFO")
    return True
  