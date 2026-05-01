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

        print(f"正在解压 SHP: 共 {num_frames} 帧, 尺寸 {g_width}x{g_height}")
        
        # 2. 读取所有的 Frame Header (24 bytes)
        frame_headers = []
        for _ in range(num_frames):
            fh = stream.read(24)
            fx, fy, fw, fh_h = struct.unpack('<HHHH', fh[0:8])
            flags = fh[8]
            offset = struct.unpack('<I', fh[20:24])[0]
            frame_headers.append((fx, fy, fw, fh_h, flags, offset))

        for fx, fy, fw, fh_h, flags, offset in frame_headers:
            base_surface = pygame.Surface((g_width, g_height), pygame.SRCALPHA)
            
            if fw == 0 or fh_h == 0 or offset == 0:
                self.frames.append(base_surface)
                continue
                
            stream.seek(offset)
            
            if (flags & 0x02) == 0:
                pixel_indices = stream.read(fw * fh_h)
            else:
                pixel_indices = self._decompress_rle_data(stream, fw, fh_h)
            
            frame_surf = pygame.Surface((fw, fh_h), pygame.SRCALPHA)
            for y in range(fh_h):
                for x in range(fw):
                    if y * fw + x < len(pixel_indices):
                        idx = pixel_indices[y * fw + x]
                        if idx != 0: # 0x00 是透明色
                            frame_surf.set_at((x, y), self.pal_colors[idx])
                      
            base_surface.blit(frame_surf, (fx, fy))
            self.frames.append(base_surface)

    def _decompress_rle_data(self, stream, frame_width, frame_height):
        """完全按照 Rust 源码 1:1 翻译的按行 RLE 解压算法"""
        decompressed_data = bytearray()
        
        for _ in range(frame_height):
            line_buffer = bytearray()
            
            row_length_bytes = stream.read(2)
            if len(row_length_bytes) < 2:
                break
            row_length = struct.unpack('<H', row_length_bytes)[0]
            
            current_byte_index = 2
            
            while current_byte_index < row_length:
                control_byte = stream.read(1)[0]
                current_byte_index += 1
                
                if control_byte == 0x00:
                    transparent_count = stream.read(1)[0]
                    current_byte_index += 1
                    line_buffer.extend(b'\x00' * transparent_count)
                else:
                    line_buffer.append(control_byte)
            
            if len(line_buffer) < frame_width:
                line_buffer.extend(b'\x00' * (frame_width - len(line_buffer)))
            elif len(line_buffer) > frame_width:
                line_buffer = line_buffer[:frame_width]
                
            decompressed_data.extend(line_buffer)
            
        return decompressed_data