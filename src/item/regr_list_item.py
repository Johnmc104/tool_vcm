import json
import os
from item.regr_item import RegrItem
from constants import VCM_REGR_FILENAME

class RegrListItem:
  def __init__(self, regrs=None):
    self.regrs = regrs if regrs is not None else []

  @classmethod
  def load_from_file(cls, path=VCM_REGR_FILENAME):
    if not os.path.exists(path):
      return cls()
    with open(path, "r") as f:
      data = json.load(f)
    regrs = [RegrItem.from_dict(item) for item in data.get("regrs", [])]
    return cls(regrs)

  def save_to_file(self, path=VCM_REGR_FILENAME):
    with open(path, "w") as f:
      json.dump({"regrs": [r.to_dict() for r in self.regrs]}, f, indent=2, ensure_ascii=False)

  def add_regr(self, regr_item):
    # 避免重复
    for r in self.regrs:
      if r.regr_id == regr_item.regr_id:
        return
    self.regrs.append(regr_item)

  def get_regr(self, regr_id):
    for r in self.regrs:
      if r.regr_id == regr_id:
        return r
    return None

  def remove_regr(self, regr_id):
    self.regrs = [r for r in self.regrs if r.regr_id != regr_id]

  def update_regr(self, regr_item):
    for idx, r in enumerate(self.regrs):
      if r.regr_id == regr_item.regr_id:
        self.regrs[idx] = regr_item
        return

  def get_regrs(self):
    return self.regrs