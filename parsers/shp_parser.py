import struct
import pygame
import io

class ShpParser:
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
        for _ in range(num_frames):
            frame_headers.append(stream.read(24))

        for i in range(num_frames):
            fh = frame_headers[i]
            
            # 精准解析帧头
            fx, fy, fw, fh_h = struct.unpack('<HHHH', fh[0:8])
            comp = fh[8]
            data_offset = struct.unpack('<I', fh[20:24])[0]
            
            base_surface = pygame.Surface((g_width, g_height), pygame.SRCALPHA)
            
            if fw == 0 or fh_h == 0:
                self.frames.append(base_surface)
                continue
                
            stream.seek(data_offset)
            compressed_data = stream.read() 
            expected_size = fw * fh_h
            
            # 分发解压算法
            if comp == 3:
                pixel_indices = self._decompress_format80_safe(compressed_data, expected_size)
            elif comp == 2:
                pixel_indices = self._decompress_rle_zero_safe(compressed_data, expected_size)
            else:
                # 兜底：如果没压缩，也保证长度安全
                pixel_indices = compressed_data[:expected_size]
                if len(pixel_indices) < expected_size:
                    pixel_indices += bytes(expected_size - len(pixel_indices))
            
            # 安全渲染到 Surface
            frame_surf = pygame.Surface((fw, fh_h), pygame.SRCALPHA)
            for y in range(fh_h):
                for x in range(fw):
                    idx = pixel_indices[y * fw + x]
                    if idx != 0: 
                        frame_surf.set_at((x, y), self.pal_colors[idx])
                        
            base_surface.blit(frame_surf, (fx, fy))
            self.frames.append(base_surface)

    def _decompress_format80_safe(self, src, expected_size):
        """真正的 LCW 算法，加入了绝对安全的越界保护"""
        dst = bytearray(expected_size)
        sp = dp = 0
        
        while sp < len(src) and dp < expected_size:
            cmd = src[sp]
            sp += 1
            
            if cmd == 0x80: 
                break
            elif (cmd & 0x80) == 0: 
                count = cmd
                if count == 0: continue
                # 安全的字节拷贝，防止切片缩小数组
                for _ in range(count):
                    if sp < len(src) and dp < expected_size:
                        dst[dp] = src[sp]
                        dp += 1
                        sp += 1
            elif (cmd & 0x40) == 0: 
                count = (cmd & 0x3F) + 3
                if sp >= len(src): break
                offset = src[sp]
                sp += 1
                pos = dp - offset
                for _ in range(count):
                    if pos >= 0 and dp < expected_size:
                        dst[dp] = dst[pos]
                    if dp < expected_size: dp += 1
                    pos += 1
            else: 
                count = (cmd & 0x3F) + 3
                if sp + 1 >= len(src): break
                offset = struct.unpack('<H', src[sp:sp+2])[0]
                sp += 2
                pos = dp - offset
                for _ in range(count):
                    if pos >= 0 and dp < expected_size:
                        dst[dp] = dst[pos]
                    if dp < expected_size: dp += 1
                    pos += 1
        return dst

    def _decompress_rle_zero_safe(self, src, expected_size):
        """Compression 2: RLEZero，加入安全保护"""
        dst = bytearray(expected_size)
        sp = dp = 0
        while sp < len(src) and dp < expected_size:
            v = src[sp]
            sp += 1
            if v == 0:
                if sp < len(src):
                    count = src[sp]
                    sp += 1
                    dp += count # 遇到0直接跳跃，保持透明
            else:
                if dp < expected_size:
                    dst[dp] = v
                    dp += 1
        return dst

    def _generate_dummy(self):
        dummy = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(dummy, (255, 0, 0), (30, 30), 20)
        self.frames.append(dummy)