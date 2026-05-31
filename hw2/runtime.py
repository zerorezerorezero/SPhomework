"""
NL 語言運行時環境
管理全局和局部作用域、變量存儲、函數定義
"""

from typing import Dict, Any, List, Optional

class Environment:
    """代表一個作用域"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.vars: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any):
        """在當前作用域定義變量"""
        self.vars[name] = value
    
    def get(self, name: str) -> Any:
        """獲取變量值，搜索整個作用域鏈"""
        if name in self.vars:
            return self.vars[name]
        
        if self.parent is not None:
            return self.parent.get(name)
        
        raise NameError(f"未定義的變量: {name}")
    
    def set(self, name: str, value: Any):
        """設置變量值，搜索整個作用域鏈"""
        if name in self.vars:
            self.vars[name] = value
        elif self.parent is not None:
            self.parent.set(name, value)
        else:
            raise NameError(f"未定義的變量: {name}")
    
    def exists(self, name: str) -> bool:
        """檢查變量是否存在"""
        if name in self.vars:
            return True
        if self.parent is not None:
            return self.parent.exists(name)
        return False


class NLFunction:
    """代表 NL 語言中的函數"""
    
    def __init__(self, name: str, parameters: List[str], body: List, environment: Environment):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = environment
    
    def __repr__(self):
        return f"<function {self.name}>"


class NLBuiltinFunction:
    """代表內置函數"""
    
    def __init__(self, name: str, func):
        self.name = name
        self.func = func
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def __repr__(self):
        return f"<builtin function {self.name}>"


class Runtime:
    """NL 語言的運行時環境"""
    
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self._setup_builtins()
    
    def _setup_builtins(self):
        """設置內置函數"""
        self.global_env.define('len', NLBuiltinFunction('len', self.builtin_len))
        self.global_env.define('type', NLBuiltinFunction('type', self.builtin_type))
        self.global_env.define('int', NLBuiltinFunction('int', self.builtin_int))
        self.global_env.define('float', NLBuiltinFunction('float', self.builtin_float))
        self.global_env.define('string', NLBuiltinFunction('string', self.builtin_string))
        self.global_env.define('bool', NLBuiltinFunction('bool', self.builtin_bool))
        self.global_env.define('range', NLBuiltinFunction('range', self.builtin_range))
    
    # ============ 內置函數實現 ============
    
    @staticmethod
    def builtin_len(obj):
        """內置 len 函數"""
        if isinstance(obj, list):
            return len(obj)
        elif isinstance(obj, str):
            return len(obj)
        else:
            raise TypeError(f"len() 不支持 {type(obj).__name__} 類型")
    
    @staticmethod
    def builtin_type(obj):
        """內置 type 函數"""
        if isinstance(obj, bool):
            return "bool"
        elif isinstance(obj, int):
            return "int"
        elif isinstance(obj, float):
            return "float"
        elif isinstance(obj, str):
            return "string"
        elif isinstance(obj, list):
            return "list"
        elif obj is None:
            return "nil"
        else:
            return "unknown"
    
    @staticmethod
    def builtin_int(obj):
        """內置 int 轉換函數"""
        if isinstance(obj, int):
            return obj
        elif isinstance(obj, float):
            return int(obj)
        elif isinstance(obj, str):
            try:
                return int(obj)
            except ValueError:
                raise ValueError(f"無法將字符串 '{obj}' 轉換為整數")
        elif isinstance(obj, bool):
            return 1 if obj else 0
        else:
            raise TypeError(f"無法將 {type(obj).__name__} 轉換為整數")
    
    @staticmethod
    def builtin_float(obj):
        """內置 float 轉換函數"""
        if isinstance(obj, float):
            return obj
        elif isinstance(obj, int):
            return float(obj)
        elif isinstance(obj, str):
            try:
                return float(obj)
            except ValueError:
                raise ValueError(f"無法將字符串 '{obj}' 轉換為浮點數")
        else:
            raise TypeError(f"無法將 {type(obj).__name__} 轉換為浮點數")
    
    @staticmethod
    def builtin_string(obj):
        """內置 string 轉換函數"""
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif isinstance(obj, (int, float)):
            return str(obj)
        elif obj is None:
            return "nil"
        elif isinstance(obj, list):
            elements = [Runtime.builtin_string(e) for e in obj]
            return "[" + ", ".join(elements) + "]"
        else:
            return str(obj)
    
    @staticmethod
    def builtin_bool(obj):
        """內置 bool 轉換函數"""
        if isinstance(obj, bool):
            return obj
        elif isinstance(obj, int):
            return obj != 0
        elif isinstance(obj, float):
            return obj != 0.0
        elif isinstance(obj, str):
            return len(obj) > 0
        elif isinstance(obj, list):
            return len(obj) > 0
        elif obj is None:
            return False
        else:
            return True
    
    @staticmethod
    def builtin_range(n):
        """內置 range 函數"""
        if not isinstance(n, int):
            raise TypeError(f"range() 期望整數，但得到 {type(n).__name__}")
        return list(range(n))
    
    # ============ 作用域管理 ============
    
    def push_environment(self) -> Environment:
        """創建新的局部作用域"""
        new_env = Environment(self.current_env)
        self.current_env = new_env
        return new_env
    
    def pop_environment(self):
        """返回到父作用域"""
        if self.current_env.parent is not None:
            self.current_env = self.current_env.parent
        else:
            raise RuntimeError("無法彈出全局作用域")
    
    def define(self, name: str, value: Any):
        """定義變量"""
        self.current_env.define(name, value)
    
    def get(self, name: str) -> Any:
        """獲取變量值"""
        return self.current_env.get(name)
    
    def set(self, name: str, value: Any):
        """設置變量值"""
        self.current_env.set(name, value)
    
    def exists(self, name: str) -> bool:
        """檢查變量是否存在"""
        return self.current_env.exists(name)


# ============ 型態檢查和轉換 ============

def nl_to_python(value):
    """將 NL 值轉換為 Python 值（用於操作）"""
    return value

def python_to_nl(value):
    """將 Python 值轉換為 NL 值"""
    return value

def is_truthy(value):
    """判斷值是否為真"""
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    elif isinstance(value, (int, float)):
        return value != 0
    elif isinstance(value, str):
        return len(value) > 0
    elif isinstance(value, list):
        return len(value) > 0
    else:
        return True
