import io

class IniParser:
    def __init__(self, data=None, filepath=None):
        """
        支持直接从 VFS 的 bytes 载入，或从本地硬盘载入
        """
        self.sections = {}
        
        if filepath:
            # 兼容读取外部自定义的 mod 文件
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                self._parse(f.read())
        elif data:
            text = data.decode('latin-1', errors='ignore')
            self._parse(text)
        else:
            raise ValueError("必须提供 data_bytes 或 filepath")

    def _parse(self, text):
        current_section = None
        
        for line in text.splitlines():
            # 1. 剔除';' 注释
            line = line.split(';')[0].strip()
            
            # 2. 跳过空行
            if not line:
                continue
                
            # 3. 解析 Section 节点 [NodeName]
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].strip()
                if current_section not in self.sections:
                    self.sections[current_section] = {}
            
            # 4. 解析 Key=Value 对
            elif current_section is not None and '=' in line:
                # 只在第一个等号处分割，防止 value 里也有等号
                key, value = line.split('=', 1)
                self.sections[current_section][key.strip()] = value.strip()
                
                
    def get_string(self, section, key, default=""):
        return self.sections.get(section, {}).get(key, default)

    def get_int(self, section, key, default=0):
        val = self.get_string(section, key)
        try:
            return int(val)
        except ValueError:
            return default

    def get_float(self, section, key, default=0.0):
        val = self.get_string(section, key)
        try:
            return float(val)
        except ValueError:
            return default

    def get_bool(self, section, key, default=False):
        val = self.get_string(section, key).lower()
        if val in ['yes', 'true', '1']:
            return True
        if val in ['no', 'false', '0']:
            return False
        return default