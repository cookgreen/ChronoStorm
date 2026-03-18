import struct
import io
import pygame
import os

class ShpParser:
    #def __init__(self, filepath, pal_colors):
    #    self.filepath = filepath
    #    self.pal_colors = pal_colors # 传入从 pal_parser 读取的 256 色列表
    #    self.frames = [] # 存储解析出的 pygame.Surface
    #    
    #    if os.path.exists(filepath):
    #        self._parse()
    #    else:
    #        print(f"Warning: {filepath} not found. Generating dummy asset.")
    #        self._generate_dummy()
            
    def __init__(self, data_bytes, pal_colors):
        self.pal_colors = pal_colors
        self.frames = []
        
        if data_bytes:
            self._parse_from_bytes(data_bytes)
        else:
            self._generate_dummy()

    def _parse_from_bytes(self, data_bytes):
        stream = io.BytesIO(data_bytes)
        
        header = stream.read(8)
        if len(header) < 8: return
        
        zero, g_width, g_height, num_frames = struct.unpack('<HHHH', header)
        if zero != 0:
            print("❌ SHP解析失败: 这不是标准的 RA2/TS SHP 格式。")
            return

        print(f"🖼️ 正在解压 SHP: 共 {num_frames} 帧, 基础尺寸 {g_width}x{g_height}")
            
        frame_headers = []
        # 2. 读取所有帧的头部信息 (每帧 24 字节)
        for _ in range(num_frames):
            f_head = stream.read(24)
            # 解析: x, y, width, height, 压缩方式(1字节), ..., 数据偏移量(最后4字节)
            fx, fy, fw, fh, comp = struct.unpack('<HHHHB', f_head[:9])
            data_offset = struct.unpack('<I', f_head[20:24])[0]
            frame_headers.append((fx, fy, fw, fh, comp, data_offset))
            
        # 3. 逐帧解压像素数据
        for fx, fy, fw, fh, comp, offset in frame_headers:
            if fw == 0 or fh == 0:
                continue
            
            stream.seek(offset)
            # 预估解压后的数据大小
            raw_data = stream.read() 
            pixel_indices = self._decode_format80(raw_data, fw * fh)
            
            # 4. 将颜色索引转换为 Pygame Surface
            surface = pygame.Surface((fw, fh), pygame.SRCALPHA)
            for y in range(fh):
                for x in range(fw):
                    idx = pixel_indices[y * fw + x]
                    if idx != 0: # 索引 0 通常是透明背景
                        color = self.pal_colors[idx]
                        surface.set_at((x, y), color)
            
            self.frames.append(surface)
        print(frame_headers)
        #print(f"Successfully loaded SHP: {self.filepath} ({len(self.frames)} frames)")

    def _parse(self):
        with open(self.filepath, 'rb') as f:
            # 1. 读取文件头 (14 字节)
            header = f.read(14)
            _, global_width, global_height, num_frames = struct.unpack('<HHHH', header[:8])
            
            frame_headers = []
            # 2. 读取所有帧的头部信息 (每帧 24 字节)
            for _ in range(num_frames):
                f_head = f.read(24)
                # 解析: x, y, width, height, 压缩方式(1字节), ..., 数据偏移量(最后4字节)
                fx, fy, fw, fh, comp = struct.unpack('<HHHHB', f_head[:9])
                data_offset = struct.unpack('<I', f_head[20:24])[0]
                frame_headers.append((fx, fy, fw, fh, comp, data_offset))
                
            # 3. 逐帧解压像素数据
            for fx, fy, fw, fh, comp, offset in frame_headers:
                if fw == 0 or fh == 0:
                    continue
                
                f.seek(offset)
                # 预估解压后的数据大小
                raw_data = f.read() 
                pixel_indices = self._decode_format80(raw_data, fw * fh)
                
                # 4. 将颜色索引转换为 Pygame Surface
                surface = pygame.Surface((fw, fh), pygame.SRCALPHA)
                for y in range(fh):
                    for x in range(fw):
                        idx = pixel_indices[y * fw + x]
                        if idx != 0: # 索引 0 通常是透明背景
                            color = self.pal_colors[idx]
                            surface.set_at((x, y), color)
                
                self.frames.append(surface)
            print(f"Successfully loaded SHP: {self.filepath} ({len(self.frames)} frames)")

    def _decode_format80(self, data, target_length):
        """Westwood Format 80 RLE 核心解压算法"""
        out = bytearray(target_length)
        src = 0
        dst = 0
        
        while src < len(data) and dst < len(out):
            cmd = data[src]
            src += 1
            
            if cmd == 0x80: # 0x80 代表指令结束
                break
            elif (cmd & 0x80) != 0: # 最高位是 1: 跳过透明像素
                count = cmd & 0x7F
                dst += count # out 数组默认是 0 (透明色)，所以直接跳过指针
            elif (cmd & 0x40) != 0: # 次高位是 1: 连续重复同一个颜色
                count = (cmd & 0x3F) + 2
                val = data[src]
                src += 1
                for _ in range(count):
                    if dst < len(out):
                        out[dst] = val
                        dst += 1
            else: # 最高位和次高位都是 0: 连续的非压缩原始像素
                count = cmd + 1
                for _ in range(count):
                    if dst < len(out) and src < len(data):
                        out[dst] = data[src]
                        dst += 1
                        src += 1
        return out

    def _generate_dummy(self):
        """如果找不到文件，生成一个占位符，保证引擎不崩溃"""
        dummy = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(dummy, (255, 0, 0), (30, 30), 20) # 画个红球代替动员兵
        self.frames.append(dummy)