import struct

class PalParser:
    def __init__(self, filepath=None):
        self.colors = []
        if filepath:
            self.load(filepath)

    def load(self, filepath):
        self.colors = []
        with open(filepath, 'rb') as f:
            pal_data = f.read(768)
            
            for i in range(256):
                r = pal_data[i * 3]
                g = pal_data[i * 3 + 1]
                b = pal_data[i * 3 + 2]
                
                standard_r = r << 2
                standard_g = g << 2
                standard_b = b << 2
                
                self.colors.append((standard_r, standard_g, standard_b))
                
    def get_color(self, index):
        if 0 <= index < len(self.colors):
            return self.colors[index]
        return (0, 0, 0)