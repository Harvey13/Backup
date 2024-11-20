from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from datetime import datetime

class LogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Journal de synchronisation")
        self.setMinimumSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
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