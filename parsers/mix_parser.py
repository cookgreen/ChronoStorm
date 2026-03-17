import struct
import os

class MixParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file_count = 0
        self.data_size = 0
        self.files = {}

        if os.path.exists(filepath):
            self._parse_header()

    def _parse_header(self):
        with open(self.filepath, 'rb') as f:
            header_data = f.read(6)
            if len(header_data) < 6:
                return
            
            self.file_count, self.data_size = struct.unpack('<HI', header_data)
            
            for _ in range(self.file_count):
                index_data = f.read(12)
                file_id, offset, size = struct.unpack('<III', index_data)
                
                actual_offset = 6 + (self.file_count * 12) + offset
                self.files[file_id] = (actual_offset, size)

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