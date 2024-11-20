from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QProgressBar, QFileDialog)
from ..models.folder_pair import FolderPair, Progress

class FolderPairWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
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
    
    def get_mapping(self) -> FolderPair:
        return FolderPair(
            source=self.source_edit.text(),
            destination=self.dest_edit.text()
        )
    
    def set_mapping(self, mapping: FolderPair):
        self.source_edit.setText(mapping.source)
        self.dest_edit.setText(mapping.destination)
    
    def update_progress(self, progress: Progress):
        self.progress.setMaximum(progress.total)
        self.progress.setValue(progress.current)
        
        if progress.status == 'error':
            self.progress.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #dc3545;
                }
            """)
        elif progress.status == 'completed':
            self.progress.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #28a745;
                }
            """)