from sim.sim_manager import SimManager
from sim.handle_add_basic_regr import handle_add_basic_regr
from sim.handle_add_basic_single import handle_add_basic_single
from sim.handle_list_sim_info import handle_list_sim_info
from sim.handle_update_node_dir import handle_update_node_dir
from sim.handle_sim_time_pass import handle_sim_time_pass

class SimService:
  def __init__(self, cursor, logger):
    self.cursor = cursor
    self.logger = logger

  def handle_add_basic_single(self, args):
    handle_add_basic_single(self.cursor, self.logger, args)

  def handle_add_basic_regr(self, args):
    handle_add_basic_regr(self.cursor, args)

  def handle_update_node_dir(self, args):
    handle_update_node_dir(self.cursor, args)

  def handle_sim_time_pass(self, args):
    handle_sim_time_pass(self.cursor, args)

  def handle_list_sim_info(self, args):
    handle_list_sim_info(self.cursor, args)