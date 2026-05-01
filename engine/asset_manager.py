import io
from parsers.mix_parser import MixParser, ra2_crc

class AssetManager:
    def __init__(self):
        self.mounted_mixes = [] 
        self.file_index = {}
        self.cache = {}

    def mount_mix(self, mix_parser, mix_name="Unknown"):
        """
        挂载一个 MIX 包，后挂载的优先级更高（用于支持 Mod 覆盖原版文件）
        """
        self.mounted_mixes.append(mix_parser)
        
        count = 0
        for file_id in mix_parser.files.keys():
            self.file_index[file_id] = mix_parser
            count += 1
            
        print(f"成功挂载 {mix_name}, 新增 {count} 个文件索引. 全局资源池: {len(self.file_index)}")

    def mount_from_filepath(self, filepath, name=None):
        """直接从硬盘文件挂载"""
        mix = MixParser(filepath)
        self.mount_mix(mix, name or filepath)

    def mount_from_bytes(self, data_bytes, name="MemoryMix"):
        mix = MixParser(data_bytes)
        self.mount_mix(mix, name)

    def get_file(self, filename: str) -> bytes:
        """
        核心 API：无视来源，直接获取文件字节流
        """
        file_id = ra2_crc(filename)

        if file_id in self.cache:
            return self.cache[file_id]

        if file_id in self.file_index:
            mix_parser = self.file_index[file_id]
            data = mix_parser.read_file(filename)
            
            if data:
                self.cache[file_id] = data
                return data
                
        print(f"资源丢失: 在所有已挂载的 MIX 中找不到 {filename}")
        return None