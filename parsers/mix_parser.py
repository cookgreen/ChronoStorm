import struct
import binascii
import io
import os

from Crypto.Cipher import Blowfish
from . import mix_const

# 提取自 ra2mix 的核心常量
PUBLIC_EXPONENT = 65537
PUBLIC_MODULUS = int(
    "681994811107118991598552881669230523074742337494683459234572860554038768387821"
    "901289207730765589"
)

class MixParser:
    def __init__(self, source):
        self.files = {}  # file_id -> (absolute_offset, size)
        self.stream = None
        
        if not source:
            raise ValueError("Source bytes are empty!")
            
        if isinstance(source, str) and os.path.exists(source):
            self.stream = open(source, 'rb')
        elif isinstance(source, bytes):
            self.stream = io.BytesIO(source)
        else:
            raise ValueError("Invalid source.")
            
        self._parse()

    def _parse(self):
        self.stream.seek(0)
        
        # 判断是老版 C&C 格式还是新版 RA2 格式
        first_word = struct.unpack("=H", self.stream.read(2))[0]
        self.stream.seek(0)
        
        if first_word != 0:
            # 未加密的老版本格式 (如提取出来的 cache.mix)
            count, data_size = struct.unpack("=HI", self.stream.read(6))
            self._parse_unencrypted(header_size=6, count=count)
        else:
            # 带有 Flags 的新版本格式 (如 ra2.mix)
            flags, count, data_size = struct.unpack("=IHI", self.stream.read(10))
            is_encrypted = (flags & 0x20000) != 0  # 真正的加密判断位！
            
            if is_encrypted:
                print("🔒 检测到 ra2.mix 加密壳，正在启动完美破译...")
                self._parse_encrypted()
            else:
                self._parse_unencrypted(header_size=10, count=count)

    def _parse_encrypted(self):
        self.stream.seek(4) # 跳过 flags
        encrypted_blowfish_key = self.stream.read(80)
        
        # 1. 极其优雅的 RSA 解密 (无视对齐，直接 rstrip 清除补零，完全复刻 ra2mix)
        blocks = [encrypted_blowfish_key[i:i+40] for i in range(0, 80, 40)]
        decrypted_blowfish_key = b""
        for encrypted_block in blocks:
            decrypted_int = pow(
                int.from_bytes(encrypted_block, byteorder="little"),
                PUBLIC_EXPONENT,
                PUBLIC_MODULUS,
            )
            decrypted = decrypted_int.to_bytes(
                (decrypted_int.bit_length() + 7) // 8, byteorder="little"
            )
            decrypted_blowfish_key += decrypted.rstrip(b"\x00")

        # 2. 回归大道至简：直接使用原生的 ECB 模式，不再画蛇添足翻转字节序！
        cipher = Blowfish.new(decrypted_blowfish_key, Blowfish.MODE_ECB)

        # 3. 读取并解密 Header (获取文件数)
        self.stream.seek(84) # 4(flags) + 80(key)
        first_block = self.stream.read(8)
        decrypted_first_block = cipher.decrypt(first_block)
        
        file_count, data_size = struct.unpack("=HI", decrypted_first_block[:6])
        print(f"🔓 MIX 破译成功！真实包含文件数: {file_count}")

        # 增加一道安全防线，如果密码还是不对导致乱码，提前拦截防止 struct.error
        if file_count > 5000:
            raise ValueError(f"❌ 解密异常：解密出的文件数为 {file_count}。字典读取已被强制终止以防止内存越界。")
        
        # 4. 精准计算解密块的 Padding (严格遵循 ra2mix 的对齐算法)
        index_len = file_count * 12
        remaining_index_len = index_len - 6
        padding_size = 8 - (remaining_index_len % 8)
        decrypt_size = remaining_index_len + padding_size
        
        # 5. 解密字典并拼接
        encrypted_index_data = self.stream.read(decrypt_size)
        decrypted_index_data = cipher.decrypt(encrypted_index_data)
        
        # 剔除尾部用于 8 字节对齐的垃圾 Padding
        if padding_size > 0:
            index_decrypted = decrypted_first_block[-2:] + decrypted_index_data[:-padding_size]
        else:
            index_decrypted = decrypted_first_block[-2:] + decrypted_index_data
        
        # 6. 计算绝对偏移并载入 VFS
        # 核心载荷起点 = 头(10) + 文件数*12 + RSA(80) + Blowfish填充
        body_start = 10 + (12 * file_count) + 80 + padding_size
        
        for i in range(file_count):
            start = i * 12
            end = start + 12
            file_id, offset, size = struct.unpack("=iII", index_decrypted[start:end])
            self.files[file_id] = (body_start + offset, size)

    def _parse_unencrypted(self, header_size, count):
        self.stream.seek(header_size)
        index_data = self.stream.read(count * 12)
        body_start = header_size + (count * 12)
        
        for i in range(count):
            start = i * 12
            end = start + 12
            file_id, offset, size = struct.unpack("=iII", index_data[start:end])
            self.files[file_id] = (body_start + offset, size)

    def read_file(self, filename):
        file_id = ra2_crc(filename)
        if file_id not in self.files:
            return None
        offset, size = self.files[file_id]
        self.stream.seek(offset)
        return self.stream.read(size)