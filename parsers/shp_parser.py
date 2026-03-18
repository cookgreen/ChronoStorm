import struct
import pygame
import io

class ShpParser:
    def __init__(self, data_bytes, pal_colors):
        self.pal_colors = pal_colors
        self.frames = []
        if data_bytes:
            self._parse_from_bytes(data_bytes)

    def _parse_from_bytes(self, data):
        stream = io.BytesIO(data)
        
        # 1. 验证 RA2/TS 格式头 (8字节)
        header = stream.read(8)
        if len(header) < 8: return
        
        zero, g_width, g_height, num_frames = struct.unpack('<HHHH', header)
        
        # RA2/TS 的 SHP 文件，首个 UInt16 必须永远是 0
        if zero != 0:
            print("❌ SHP解析失败: 这不是标准的 RA2/TS SHP 格式 (第一位不为0)。")
            return

        print(f"🖼️ 正在解压 SHP: 共 {num_frames} 帧, 基础尺寸 {g_width}x{g_height}")
        
        # 2. 提取所有帧头 (每帧固定 24 字节)
        frame_headers = []
        for _ in range(num_frames):
            frame_headers.append(stream.read(24))

        # 3. 逐帧解码
        for i in range(num_frames):
            fh = frame_headers[i]
            # 我们只需要前 22 字节来获取核心参数，忽略最后 2 个不知名填充
            x, y, w, h, comp, pad, radar, zero_pad, offset = struct.unpack('<HHHHBBIII', fh[:22])
            
            # 创建一个全尺寸的透明画板，保证每一帧动画的重心绝对居中，防止单位抽搐
            base_surface = pygame.Surface((g_width, g_height), pygame.SRCALPHA)
            
            if w == 0 or h == 0:
                self.frames.append(base_surface)
                continue
                
            stream.seek(offset)
            
            # Format 80 自带 0x80 结束符，所以我们直接把后续数据全喂给它
            compressed_data = stream.read() 
            
            # RA2 的单位通常使用 Compression 3 (Format 80 LCW 压缩)
            if comp == 3:
                pixel_indices = self._decompress_format80(compressed_data, w * h)
            elif comp == 1:
                pixel_indices = compressed_data[:w*h]
            else:
                print(f"⚠️ 警告: 第 {i} 帧使用了未知的压缩格式 {comp}")
                pixel_indices = bytes(w * h)
            
            # 4. 根据调色板绘制像素
            frame_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            
            for py in range(h):
                for px in range(w):
                    idx = pixel_indices[py * w + px]
                    if idx != 0: # 索引 0 是红警里的绝对透明色
                        color = self.pal_colors[idx]
                        frame_surf.set_at((px, py), color)
                        
            # 把解码好的局部帧，按照 X/Y 偏移量贴到全局透明画板上
            base_surface.blit(frame_surf, (x, y))
            self.frames.append(base_surface)
            
    def _decompress_format80(self, src, expected_size):
        """复刻 Westwood 祖传的 LCW (Format 80) 字典解压算法"""
        dst = bytearray(expected_size)
        sp = 0
        dp = 0
        
        while sp < len(src) and dp < expected_size:
            cmd = src[sp]
            sp += 1
            
            if cmd == 0x80: 
                # 1000 0000: 结束指令
                break
            elif (cmd & 0x80) == 0: 
                # 0xxx xxxx: 直接复制后续的 cmd 个明文字节
                count = cmd
                if count == 0: continue
                dst[dp:dp+count] = src[sp:sp+count]
                sp += count
                dp += count
            elif (cmd & 0x40) == 0: 
                # 10xx xxxx: 相对短偏移复制 (从已解压的字典里抄作业)
                count = (cmd & 0x3F) + 3
                offset = src[sp]
                sp += 1
                pos = dp - offset
                for _ in range(count):
                    if pos >= 0: dst[dp] = dst[pos]
                    dp += 1; pos += 1
            else: 
                # 11xx xxxx: 相对长偏移复制 (从很远的地方抄作业)
                count = (cmd & 0x3F) + 3
                offset = struct.unpack('<H', src[sp:sp+2])[0]
                sp += 2
                pos = dp - offset
                for _ in range(count):
                    if pos >= 0: dst[dp] = dst[pos]
                    dp += 1; pos += 1
                    
        return dst