import json
from pathlib import Path
from utils.reason import get_order_reason
from utils.util import write_json
import re

a = re.match(r'第[一二三四五六七八九十百千]+章', '第四章 （刪除）')
print(a)