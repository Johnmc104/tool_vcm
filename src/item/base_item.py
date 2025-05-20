import json
import os

class BaseItem:
  @classmethod
  def load_from_file(cls, path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
      return None
    with open(path, "r") as f:
      data = json.load(f)
    return cls.from_dict(data)

  def save_to_file(self, path):
    with open(path, "w") as f:
      json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

  def to_dict(self):
    raise NotImplementedError

  @classmethod
  def from_dict(cls, data):
    raise NotImplementedError