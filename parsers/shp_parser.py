import struct
import pygame
import io

class ShpParser:
    def __init__(self, data_bytes, pal_colors):
        self.pal_colors = pal_colors
        self.frames = []
        if data_bytes:
            self._parse_from_bytes(data_bytes)

    def _parse_from_bytes(self, data_bytes):
        stream = io.BytesIO(data_bytes)
        
        # 1. 解析全局 Header (8 bytes)
        header = stream.read(8)
        if len(header) < 8: return
        reserved, g_width, g_height, num_frames = struct.unpack('<HHHH', header)

        print(f"🖼️ 正在按 Rust 逻辑解压 SHP: 共 {num_frames} 帧, 尺寸 {g_width}x{g_height}")
        
        # 2. 读取所有的 Frame Header (24 bytes)
        frame_headers = []
        for _ in range(num_frames):
            fh = stream.read(24)
            # 严格按照 Rust 结构体提取
            fx, fy, fw, fh_h = struct.unpack('<HHHH', fh[0:8])
            flags = fh[8]
            # 第 20-23 字节是 offset
            offset = struct.unpack('<I', fh[20:24])[0]
            frame_headers.append((fx, fy, fw, fh_h, flags, offset))

        # 3. 逐帧解析
        for fx, fy, fw, fh_h, flags, offset in frame_headers:
            # 创建底板画布 (全局宽高)
            base_surface = pygame.Surface((g_width, g_height), pygame.SRCALPHA)
            
            # 如果是空帧或者没有偏移量，直接放入空画布
            if fw == 0 or fh_h == 0 or offset == 0:
                self.frames.append(base_surface)
                continue
                
            stream.seek(offset)
            
            # 判断是否压缩 (对应 Rust 的 flags & 0x02 == 0)
            if (flags & 0x02) == 0:
                # 未压缩：直接读取 width * height 长度的数据
                pixel_indices = stream.read(fw * fh_h)
            else:
                # RLE 压缩：调用翻译自 Rust 的解压函数
                pixel_indices = self._decompress_rle_data(stream, fw, fh_h)
            
            # 4. 渲染像素
            frame_surf = pygame.Surface((fw, fh_h), pygame.SRCALPHA)
            for y in range(fh_h):
                for x in range(fw):
                    # 确保不越界
                    if y * fw + x < len(pixel_indices):
                        idx = pixel_indices[y * fw + x]
                        if idx != 0: # 0x00 是透明色
                            frame_surf.set_at((x, y), self.pal_colors[idx])
                            
            # 拼合偏移量
            base_surface.blit(frame_surf, (fx, fy))
            self.frames.append(base_surface)

    def _decompress_rle_data(self, stream, frame_width, frame_height):
        """完全按照 Rust 源码 1:1 翻译的按行 RLE 解压算法"""
        decompressed_data = bytearray()
        
        for _ in range(frame_height):
            line_buffer = bytearray()
            
            # 读取该行压缩后的总长度 (2 bytes)
            row_length_bytes = stream.read(2)
            if len(row_length_bytes) < 2:
                break
            row_length = struct.unpack('<H', row_length_bytes)[0]
            
            # 已经读取了两个字节的行长度
            current_byte_index = 2
            
            while current_byte_index < row_length:
                # Python 读单个 byte 取 [0] 就是整数
                control_byte = stream.read(1)[0]
                current_byte_index += 1
                
                if control_byte == 0x00:
                    # 0x00 代表透明，接下来一个字节是透明像素的个数
                    transparent_count = stream.read(1)[0]
                    current_byte_index += 1
                    line_buffer.extend(b'\x00' * transparent_count)
                else:
                    line_buffer.append(control_byte)
            
            # Westwood 抠门优化：补齐不足 frame_width 的末尾透明像素
            if len(line_buffer) < frame_width:
                line_buffer.extend(b'\x00' * (frame_width - len(line_buffer)))
            elif len(line_buffer) > frame_width:
                # 安全兜底，防止意外超出
                line_buffer = line_buffer[:frame_width]
                
            decompressed_data.extend(line_buffer)
            
        return decompressed_data