import struct
import os

class MixParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.files = {} # { file_id: (offset, size) }
        
        if os.path.exists(filepath):
            self._parse_header()

    def _parse_header(self):
        with open(self.filepath, 'rb') as f:
            header_data = f.read(6)
            file_count, data_size = struct.unpack('<HI', header_data)
            
            for _ in range(file_count):
                index_data = f.read(12)
                file_id, offset, size = struct.unpack('<III', index_data)
                actual_offset = 6 + (file_count * 12) + offset
                self.files[file_id] = (actual_offset, size)

    def calculate_id(self, filename):
        crc = 0
        for char in filename.upper():
            crc = ((crc << 1) | (crc >> 31)) & 0xFFFFFFFF
            crc ^= ord(char)
        return crc

    def extract(self, filename, output_path):
        file_id = self.calculate_id(filename)
        
        if file_id not in self.files:
            print(f"File {filename} (ID: {file_id}) not found in {self.filepath}")
            return False
            
        offset, size = self.files[file_id]
        with open(self.filepath, 'rb') as f:
            f.seek(offset)
            data = f.read(size)
            
            with open(output_path, 'wb') as out_f:
                out_f.write(data)
        print(f"Extracted: {filename} -> {output_path}")
        return True
    
    def extract_file_by_id(self, file_id, output_path):
        if file_id not in self.files:
            print(f"File ID {file_id} not found in {self.filepath}")
            return False
            
        offset, size = self.files[file_id]
        with open(self.filepath, 'rb') as f:
            f.seek(offset)
            data = f.read(size)
            
            with open(output_path, 'wb') as out_f:
                out_f.write(data)
        return True