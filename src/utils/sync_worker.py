import os
import shutil
import zlib
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
from ..models.folder_pair import Progress

class SyncWorker(QThread):
    progress = pyqtSignal(int, Progress)  # mapping_index, progress
    log_entry = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, mappings):
        super().__init__()
        self.mappings = mappings

    def calculate_crc32(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                return format(zlib.crc32(f.read()) & 0xFFFFFFFF, '08x')
        except Exception as e:
            print(f"Error calculating CRC for {filepath}: {e}")
            return None

    def run(self):
        for idx, mapping in enumerate(self.mappings):
            try:
                if not os.path.exists(mapping.source):
                    raise FileNotFoundError(f"Le dossier source n'existe pas: {mapping.source}")
                
                if not os.path.exists(mapping.destination):
                    os.makedirs(mapping.destination)
                
                files = [f for f in os.listdir(mapping.source) 
                        if os.path.isfile(os.path.join(mapping.source, f))]
                
                progress = Progress(0, len(files), 'syncing')
                self.progress.emit(idx, progress)
                
                for i, file in enumerate(files):
                    src_path = os.path.join(mapping.source, file)
                    dst_path = os.path.join(mapping.destination, file)
                    
                    try:
                        if os.path.exists(dst_path):
                            src_crc = self.calculate_crc32(src_path)
                            dst_crc = self.calculate_crc32(dst_path)
                            
                            if src_crc != dst_crc:
                                base, ext = os.path.splitext(file)
                                counter = 1
                                while os.path.exists(dst_path):
                                    new_name = f"{base}_{counter:03d}{ext}"
                                    dst_path = os.path.join(mapping.destination, new_name)
                                    counter += 1
                                
                                shutil.copy2(src_path, dst_path)
                                self.log_entry.emit({
                                    'type': 'renamed',
                                    'original_name': file,
                                    'new_name': os.path.basename(dst_path),
                                    'source': src_path,
                                    'destination': dst_path,
                                    'timestamp': datetime.now().isoformat()
                                })
                        else:
                            shutil.copy2(src_path, dst_path)
                            self.log_entry.emit({
                                'type': 'copied',
                                'name': file,
                                'source': src_path,
                                'destination': dst_path,
                                'timestamp': datetime.now().isoformat()
                            })
                        
                        progress.current = i + 1
                        self.progress.emit(idx, progress)
                        
                    except Exception as e:
                        self.log_entry.emit({
                            'type': 'error',
                            'file': file,
                            'source': src_path,
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        })
                
                progress.status = 'completed'
                self.progress.emit(idx, progress)
                        
            except Exception as e:
                self.log_entry.emit({
                    'type': 'error',
                    'source': mapping.source,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                progress = Progress(0, 1, 'error')
                self.progress.emit(idx, progress)
        
        self.finished.emit()