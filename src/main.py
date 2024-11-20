import sys
import os
import json
import shutil
import zlib
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog,
    QScrollArea, QDialog, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class SyncWorker(QThread):
    progress = pyqtSignal(int, int, int)  # mapping_index, current, total
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
                source = mapping['source']
                dest = mapping['destination']
                
                if not os.path.exists(source):
                    raise FileNotFoundError(f"Le dossier source n'existe pas: {source}")
                
                if not os.path.exists(dest):
                    os.makedirs(dest)
                
                files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
                self.progress.emit(idx, 0, len(files))
                
                for i, file in enumerate(files):
                    src_path = os.path.join(source, file)
                    dst_path = os.path.join(dest, file)
                    
                    try:
                        if os.path.exists(dst_path):
                            src_crc = self.calculate_crc32(src_path)
                            dst_crc = self.calculate_crc32(dst_path)
                            
                            if src_crc != dst_crc:
                                base, ext = os.path.splitext(file)
                                counter = 1
                                while os.path.exists(dst_path):
                                    new_name = f"{base}_{counter:03d}{ext}"
                                    dst_path = os.path.join(dest, new_name)
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
                        
                        self.progress.emit(idx, i + 1, len(files))
                        
                    except Exception as e:
                        self.log_entry.emit({
                            'type': 'error',
                            'file': file,
                            'source': src_path,
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        })
                        
            except Exception as e:
                self.log_entry.emit({
                    'type': 'error',
                    'source': source,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                self.progress.emit(idx, 0, 1)
        
        self.finished.emit()

class LogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Journal de synchronisation")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.log_text)
        
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
    def add_log(self, entry):
        timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        html = f"<p><strong>[{timestamp}]</strong> "
        
        if entry['type'] == 'error':
            html += f'<span style="color: #dc3545;">ERREUR: {entry["error"]}</span>'
        elif entry['type'] == 'renamed':
            html += f'<span style="color: #ffc107;">Renommé: {entry["original_name"]} → {entry["new_name"]}</span>'
        else:
            html += f'<span style="color: #28a745;">Copié: {entry["name"]}</span>'
        
        html += f'<br><span style="color: #6c757d;">Source: {entry["source"]}</span>'
        if 'destination' in entry:
            html += f'<br><span style="color: #6c757d;">Destination: {entry["destination"]}</span>'
        
        html += "</p>"
        self.log_text.append(html)

class FolderPairWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
                margin: 4px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Chemins
        paths_layout = QHBoxLayout()
        
        # Source
        source_layout = QVBoxLayout()
        source_label = QLabel("Dossier source (Smartphone):")
        source_label.setStyleSheet("font-weight: bold;")
        source_layout.addWidget(source_label)
        
        self.source_edit = QLineEdit()
        source_browse = QPushButton("Parcourir")
        source_h_layout = QHBoxLayout()
        source_h_layout.addWidget(self.source_edit)
        source_h_layout.addWidget(source_browse)
        source_layout.addLayout(source_h_layout)
        
        # Destination
        dest_layout = QVBoxLayout()
        dest_label = QLabel("Dossier destination (PC):")
        dest_label.setStyleSheet("font-weight: bold;")
        dest_layout.addWidget(dest_label)
        
        self.dest_edit = QLineEdit()
        dest_browse = QPushButton("Parcourir")
        dest_h_layout = QHBoxLayout()
        dest_h_layout.addWidget(self.dest_edit)
        dest_h_layout.addWidget(dest_browse)
        dest_layout.addLayout(dest_h_layout)
        
        source_browse.clicked.connect(lambda: self.browse_folder(self.source_edit))
        dest_browse.clicked.connect(lambda: self.browse_folder(self.dest_edit))
        
        paths_layout.addLayout(source_layout)
        paths_layout.addLayout(dest_layout)
        
        layout.addLayout(paths_layout)
        
        # Barre de progression
        self.progress = QProgressBar()
        self.progress.setFormat("%v/%m fichiers (%p%)")
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
    
    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if folder:
            line_edit.setText(folder)
    
    def get_mapping(self):
        return {
            'source': self.source_edit.text(),
            'destination': self.dest_edit.text()
        }
    
    def set_mapping(self, mapping):
        self.source_edit.setText(mapping['source'])
        self.dest_edit.setText(mapping['destination'])
    
    def update_progress(self, current, total):
        self.progress.setMaximum(total)
        self.progress.setValue(current)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synchronisation Smartphone")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton#syncButton {
                background-color: #28a745;
            }
            QPushButton#syncButton:hover {
                background-color: #218838;
            }
        """)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        
        # Titre
        title_layout = QHBoxLayout()
        title_label = QLabel("Synchronisation Smartphone → PC")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #212529;
            margin: 16px 0;
        """)
        title_layout.addWidget(title_label)
        main_layout.addLayout(title_layout)
        
        # Zone de défilement pour les mappings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.mappings_layout = QVBoxLayout()
        scroll_widget.setLayout(self.mappings_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Ajouter un mapping")
        sync_button = QPushButton("Synchroniser")
        sync_button.setObjectName("syncButton")
        save_button = QPushButton("Sauvegarder")
        log_button = QPushButton("Journal")
        
        add_button.clicked.connect(self.add_mapping)
        sync_button.clicked.connect(self.start_sync)
        save_button.clicked.connect(self.save_mappings)
        log_button.clicked.connect(self.show_log)
        
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(sync_button)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(log_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        
        main_widget.setLayout(main_layout)
        
        self.mapping_widgets = []
        self.log_entries = []
        self.log_dialog = LogDialog(self)
        
        # Charger les mappings sauvegardés
        self.load_mappings()
    
    def add_mapping(self):
        widget = FolderPairWidget()
        self.mapping_widgets.append(widget)
        self.mappings_layout.addWidget(widget)
    
    def save_mappings(self):
        try:
            mappings = [w.get_mapping() for w in self.mapping_widgets]
            config_dir = os.path.expanduser('~/.sync_smartphone')
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, 'mappings.json')
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Succès", "Les mappings ont été sauvegardés avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def load_mappings(self):
        try:
            config_file = os.path.expanduser('~/.sync_smartphone/mappings.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
            else:
                # Mappings par défaut
                mappings = [
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\DCIM\\Camera',
                        'destination': 'D:\\Images\\e-port huawei appareil photo N°4'
                    },
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Pictures\\Screenshots',
                        'destination': 'D:\\Images\\e-port huawei capture d\'écran'
                    },
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\WhatsApp\\Media\\WhatsApp Images',
                        'destination': 'D:\\Images\\e-port huawei a WhatsApp images N°4'
                    },
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\WhatsApp\\Media\\WhatsApp Video',
                        'destination': 'D:\\Vidéos\\e-port huawei whatsApp vidéos'
                    },
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Download',
                        'destination': 'D:\\Images\\e-port huawei aTéléchargements N°2'
                    },
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Mémoire de stockage interne\\Pictures',
                        'destination': 'D:\\Images\\e-port huawei messages textos'
                    },
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Pictures\\autres',
                        'destination': 'D:\\Images\\e-port huawei Autres'
                    },
                    {
                        'source': 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Pictures\\nikie',
                        'destination': 'D:\\Images\\e-port huawei Nikie'
                    }
                ]
            
            for mapping in mappings:
                widget = FolderPairWidget()
                widget.set_mapping(mapping)
                self.mapping_widgets.append(widget)
                self.mappings_layout.addWidget(widget)
                
        except Exception as e:
            QMessageBox.warning(self, "Attention", f"Erreur lors du chargement des mappings: {str(e)}")
    
    def start_sync(self):
        mappings = [w.get_mapping() for w in self.mapping_widgets]
        
        # Vérification des chemins
        invalid_mappings = []
        for mapping in mappings:
            if not mapping['source'] or not mapping['destination']:
                invalid_mappings.append("Chemins vides")
            elif not os.path.exists(mapping['source']):
                invalid_mappings.append(f"Source introuvable: {mapping['source']}")
        
        if invalid_mappings:
            QMessageBox.critical(self, "Erreur", 
                "Erreurs dans les mappings:\n" + "\n".join(invalid_mappings))
            return
        
        self.worker = SyncWorker(mappings)
        self.worker.progress.connect(self.update_progress)
        self.worker.log_entry.connect(self.add_log_entry)
        self.worker.finished.connect(self.sync_finished)
        self.worker.start()
    
    def update_progress(self, mapping_index, current, total):
        if 0 <= mapping_index < len(self.mapping_widgets):
            self.mapping_widgets[mapping_index].update_progress(current, total)
    
    def add_log_entry(self, entry):
        self.log_entries.append(entry)
        self.log_dialog.add_log(entry)
    
    def sync_finished(self):
        QMessageBox.information(self, "Terminé", "La synchronisation est terminée.")
        for widget in self.mapping_widgets:
            widget.progress.reset()
    
    def show_log(self):
        self.log_dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())