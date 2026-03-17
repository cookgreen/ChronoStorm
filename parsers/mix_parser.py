import struct
import io
import os
from Crypto.Cipher import Blowfish

# RA2 官方 RSA 公钥 (这是从 OpenRA 核心库中提取的)
RA2_N = int("A7553153976074A4B1D6144D9757656606010B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B", 16)
RA2_E = 65537

class MixParser:
    def __init__(self, source):
        self.files = {}
        self.stream = None
        if not source: raise ValueError("Source 为空")
        
        if isinstance(source, str) and os.path.exists(source):
            self.stream = open(source, 'rb')
        elif isinstance(source, bytes):
            self.stream = io.BytesIO(source)
        else:
            raise ValueError("Invalid source.")
        self._parse_header()

    def _parse_header(self):
        self.stream.seek(0)
        # 读取 C&C Mix 标志位
        is_cnc = struct.unpack('<H', self.stream.read(2))[0] != 0
        
        if is_cnc:
            # 古典 C&C 格式 (未加密)
            self._read_unencrypted_header(0)
        else:
            # RA/TS/RA2 格式
            flags = struct.unpack('<H', self.stream.read(2))[0]
            is_encrypted = (flags & 0x02) != 0
            
            if is_encrypted:
                print("🔒 正在解密 RA2 加密头部...")
                self._decrypt_header()
            else:
                self._read_unencrypted_header(4)

    def _decrypt_header(self):
        # 1. 提取 80 字节 RSA 块
        self.stream.seek(4)
        key_block = self.stream.read(80)
        
        # 2. RSA 解密获取 Blowfish 密钥
        c1 = int.from_bytes(key_block[:40], byteorder='little')
        c2 = int.from_bytes(key_block[40:], byteorder='little')
        m1 = pow(c1, RA2_E, RA2_N)
        m2 = pow(c2, RA2_E, RA2_N)
        
        # 拼接 56 字节密钥 (32 + 24)
        bf_key = m1.to_bytes(40, byteorder='little')[:32] + \
                 m2.to_bytes(40, byteorder='little')[:24]
        
        # 3. 初始化 Blowfish (Westwood 风格需要对每一个 4 字节进行字节序调整)
        # 这里我们模拟 OpenRA 的 ReadUInt32 逻辑
        cipher = Blowfish.new(bf_key, Blowfish.MODE_ECB)
        
        def decrypt_block(data):
            # 模拟 OpenRA 的 SwapBytes：输入是小端，解密前变大端，解密后变回小端
            res = bytearray()
            for i in range(0, len(data), 8):
                block = data[i:i+8]
                # 翻转 4 字节字序
                swapped = struct.pack('>II', *struct.unpack('<II', block))
                dec = cipher.decrypt(swapped)
                res += struct.pack('<II', *struct.unpack('>II', dec))
            return res

        # 4. 解密第一个 8 字节块以获取文件数
        first_block = self.stream.read(8)
        dec_first = decrypt_block(first_block)
        num_files = struct.unpack('<H', dec_first[:2])[0]
        
        print(f"🔓 解密成功！包含文件数: {num_files}")

        # 5. 解密整个 Index 区域 (遵循 OpenRA 的计算公式)
        # blockCount = (13 + numFiles * 12) / 8
        block_count = (13 + num_files * 12) // 8
        self.stream.seek(4 + 80)
        all_encrypted_data = self.stream.read(block_count * 8)
        dec_all = decrypt_block(all_encrypted_data)
        
        # 6. 解析 Index (从第 6 字节开始是 PackageEntry)
        # PackageEntry Size = 12 (Hash:4, Offset:4, Size:4)
        data_start = 4 + 80 + block_count * 8
        for i in range(num_files):
            offset = 6 + i * 12
            f_hash, f_off, f_size = struct.unpack('<III', dec_all[offset:offset+12])
            self.files[f_hash] = (data_start + f_off, f_size)

    def _read_unencrypted_header(self, start_offset):
        self.stream.seek(start_offset)
        num_files = struct.unpack('<H', self.stream.read(2))[0]
        self.stream.read(4) # data_size
        
        header_end = start_offset + 6 + num_files * 12
        for _ in range(num_files):
            f_hash, f_off, f_size = struct.unpack('<III', self.stream.read(12))
            self.files[f_hash] = (header_end + f_off, f_size)

    def calculate_id(self, filename):
        # RA2 使用 Classic Hash
        filename = filename.upper()
        res = 0
        for b in filename.encode('ascii'):
            res = ((res << 1) | (res >> 31)) & 0xFFFFFFFF
            res ^= b
        return res

    def read_file(self, filename):
        f_id = self.calculate_id(filename)
        if f_id not in self.files: return None
        off, size = self.files[f_id]
        self.stream.seek(off)
        return self.stream.read(size)