import struct
import pygame
import os

class ShpParser:
    def __init__(self, filepath, pal_colors):
        self.filepath = filepath
        self.pal_colors = pal_colors 
        self.frames = []
        
        if os.path.exists(filepath):
            self._parse()
        else:
            print(f"Warning: {filepath} not found. Generating dummy asset.")
            self._generate_dummy()

    def _parse(self):
        with open(self.filepath, 'rb') as f:
            header = f.read(14)
            _, global_width, global_height, num_frames = struct.unpack('<HHHH', header[:8])
            
            frame_headers = []
            for _ in range(num_frames):
                f_head = f.read(24)
                
                fx, fy, fw, fh, comp = struct.unpack('<HHHHB', f_head[:9])
                data_offset = struct.unpack('<I', f_head[20:24])[0]
                frame_headers.append((fx, fy, fw, fh, comp, data_offset))
                
            for fx, fy, fw, fh, comp, offset in frame_headers:
                if fw == 0 or fh == 0:
                    continue
                
                f.seek(offset)
                raw_data = f.read() 
                pixel_indices = self._decode_format80(raw_data, fw * fh)
                
                surface = pygame.Surface((fw, fh), pygame.SRCALPHA)
                for y in range(fh):
                    for x in range(fw):
                        idx = pixel_indices[y * fw + x]
                        if idx != 0: 
                            color = self.pal_colors[idx]
                            surface.set_at((x, y), color)
                
                self.frames.append(surface)
            print(f"Successfully loaded SHP: {self.filepath} ({len(self.frames)} frames)")

    def _decode_format80(self, data, target_length):
        out = bytearray(target_length)
        src = 0
        dst = 0
        
        while src < len(data) and dst < len(out):
            cmd = data[src]
            src += 1
            
            if cmd == 0x80:
                break
            elif (cmd & 0x80) != 0:
                count = cmd & 0x7F
                dst += count
            elif (cmd & 0x40) != 0:
                count = (cmd & 0x3F) + 2
                val = data[src]
                src += 1
                for _ in range(count):
                    if dst < len(out):
                        out[dst] = val
                        dst += 1
            else: 
                count = cmd + 1
                for _ in range(count):
                    if dst < len(out) and src < len(data):
                        out[dst] = data[src]
                        dst += 1
                        src += 1
        return out

    def _generate_dummy(self):
        dummy = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(dummy, (255, 0, 0), (30, 30), 20) # 画个红球代替动员兵
        self.frames.append(dummy)