from utils.utils_case import get_info_from_emc, gen_case_list_from_emc, caselist_lint
from utils.utils_git import get_module_name
from module.module_manager import ModuleManager
from case.case_manager import CaseManager
import os
from constants import get_current_user
from utils.utils_case import find_case_sw_info
from utils.utils_lib import rm_vcm_fail_file, add_vcm_fail_file
from utils.utils_env import check_regr_comp_result
from utils.utils_log import Logger
from item.regr_list_item import RegrListItem
from utils.utils_format import print_regr_case_status
from constants import VCM_REGR_FILENAME


class InfoService:
  """
  This class provides methods to retrieve information about the VCM system.
  """

  def __init__(self, cursor, logger: Logger):
    self.cursor = cursor
    self.logger = logger
    self.module_manager = ModuleManager(cursor)
    self.case_manager = CaseManager(cursor)

  def _handle_caselist(self, args):
    """
    Handle the 'caselist' command to check if a case list exists.

    Parameters:
      args: argparse parsed arguments object containing the case list name and module name.

    Returns:
      None
    """

    # check file vcm.fail, if exist, rm it
    status_log  = rm_vcm_fail_file("vcm.caselist.fail")
    
    # check case_list name
    if args.caselist_name is not None:
      caselist_name = args.caselist_name
    else:
      print("[VCM] Error: Case list name is required.")
      add_vcm_fail_file(status_log, "Error: Case list name is required.")
      return

    # check module_name, if not provided, get from git
    module_name = get_module_name(args)
    module_id = self.module_manager.find_module_id_by_name(module_name)
    if not module_id:
      print(f"[VCM] Error: Module '{module_name}' does not exist.")
      add_vcm_fail_file(status_log, f"Error: Module '{module_name}' does not exist.")
      return
    
    # Check if the case list name is valid
    cases, status = caselist_lint(caselist_name, module_name)
    if status is False:
      print(f"[VCM] Error: please check case_list '{caselist_name}' and fix problems.")
      #create vcm_fail_file
      add_vcm_fail_file(status_log, f"Error: please check case_list '{caselist_name}' and fix problems.")
      return

    for case_name in cases:
      # Check if the case exists in the database
      if self.case_manager.exist_case(case_name, module_id) is False:
        print(f"[VCM] Error: Case '{case_name}' not found in module '{module_name}'.")
        self.case_manager.add_case_basic(case_name, module_id, get_current_user())
        case_id = self.case_manager.find_case_id_by_module_id(case_name, module_id)
        group_name, case_c_name = find_case_sw_info(case_name)
        if not group_name or not case_c_name:
          print(f"[VCM] Warning: Case '{case_name}' not found in case_info.")
          continue
        else:
          self.case_manager.update_case_st(case_id, group_name, case_c_name)
        print(f"[VCM] Case '{case_name}' added under module '{module_name}'.")

  def _handle_emclist(self, args):
    emc_info = get_info_from_emc(args.emc_name)
    #print(f"[VCM] EMC info: {emc_info}")
    if not emc_info:
      print(f"[VCM] Error: emc_info null.")
      return
    for emc in emc_info:
      print(f"[VCM] EMC name: {emc['names']}")
      print(f"[VCM] EMC count: {emc['count']}")
      print(f"[VCM] EMC arguments: {emc['arguments']}")
      print(f"[VCM] EMC tags: {emc['tags']}")
      print("-" * 20)
    
  def _handle_createlist(self, args):
    gen_case_list_from_emc(args.emc_name)

  def _handle_checkcomp(self, args):
    current_dir = os.getcwd()
    if os.path.basename(current_dir) not in ("slurm", "regr"):
      print(f"[VCM] Error: Current directory '{current_dir}' is not 'slurm/regr'.")
      return

    status_log = rm_vcm_fail_file("vcm.checkcomp.fail")

    result = check_regr_comp_result(self.logger, args.part_name, args.part_mode, args.node_name, args.work_name)
    if result is False:
      add_vcm_fail_file(status_log, "Error: Compilation failure detected.")
      print(f"[VCM] Error: Compile failure was detected.")
      return
    else:
      print(f"[VCM] Compile successful.")

  def _handle_regrlist(self, args):
    """
    """

    # check regr_list file exist
    if not os.path.exists(VCM_REGR_FILENAME):
      self.logger.log("No regression list file found.", level="ERROR")
      return

    # Check if the regression ID exists
    regr_list = RegrListItem.load_from_file()
    if not regr_list:
      self.logger.log("No regression list found.", level="ERROR")
      return
    
    print_regr_case_status(regr_list)
    