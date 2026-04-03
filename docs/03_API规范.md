# 03 API规范（模块接口定义）

**参考02目录**：定义 modules/*.py 函数签名，确保调用一致，无状态依赖。

## 接口规范（伪代码示例）
### recorder.py
```python
class Recorder:
    def add_single_number(self, number: str, source: str) -> Dict[str, int | List[str]]:
        # 单条录入+去重，返回 {'new_count': 0|1, 'dup_count': 0|1, 'dup_numbers': []|[number]}

    def add_batch(self, file_path: str) -> Dict[str, int | List[str] | str]:
        # 批量 Excel(.xlsx)/CSV，读取'number'列，循环add_single，累积统计
        # Args: file_path str (相对/绝对)
        # Returns: {'new_count': int, 'dup_count': int, 'dup_numbers': list[str] (unique), 'file': str}
        # 示例: {'new_count': 4, 'dup_count': 1, 'dup_numbers': ['13800138000'], 'file': 'test.xlsx'}
        # 异常: 文件不存在/无效扩展/空/非'number'列 → {'new_count':0,... 'file':str}
        # 防护: try pandas.read + dropna/isdigit, tqdm进度
```

### query.py [x implemented]
```python
class Query:
    def lookup_single(self, phone: str) -> Dict[str, Optional[str]|int|List[str]]:
        # {'phone': str, 'first_seen': str|None, 'dup_count': int, 'sources': list[str]}
    
    def lookup_batch(self, file_path: str) -> Dict[str, List[Dict]|int|str]:
        # {'results': list[dict], 'processed': int, 'file': str}
        # 读取xlsx/csv 'number'列, 循环single lookup
        # 示例: {'results': [{'phone':'138...', 'dup_count':2, 'sources':['test.xlsx']}], ...}
```


### assigner.py
```python
def assign_phone(phone: str, type_: str, date: str, amount: float) -> bool:
    pass

def batch_assign(phones: dict) -> int:  # {phone: {'type':str,...}}
    pass
```

### stats.py
```python
def generate_report(start: str, end: str) -> pd.DataFrame:
    # 列: time, new, dup, rate, total_amount
    pass

def export_report(df: pd.DataFrame, path: str, fmt: str='xlsx') -> bool:
    pass
```

## 注意事项
- 输入：phone str(11位数字)，date 'YYYY-MM-DD'，amount float>0。
- 输出：dict/DataFrame，异常raise ValueError。
- 扩展：未来REST API wrapper。

## 检查
- 类型提示全覆盖。
- 事务：DB操作用with conn。

**防护**：input type检查，边界空list返回空df。
