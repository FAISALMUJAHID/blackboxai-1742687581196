import sys
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, 
                            QTextEdit, QMessageBox, QProgressBar, QStatusBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from browser_manager import BrowserManager
from utils import validate_inputs
from profiles import ProfileManager

class BrowserWorker(QThread):
    """Worker thread for browser automation"""
    log_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, instance_id, url, proxy, min_time, max_time):
        super().__init__()
        self.instance_id = instance_id
        self.url = url
        self.proxy = proxy
        self.min_time = min_time
        self.max_time = max_time
        self.browser_manager = BrowserManager(ProfileManager())

    def run(self):
        try:
            self.browser_manager.launch_browser_instance(
                self.instance_id,
                self.url,
                self.proxy,
                self.min_time,
                self.max_time,
                self.log_signal.emit
            )
        except Exception as e:
            self.error_signal.emit(f"Instance {self.instance_id} error: {str(e)}")
        finally:
            self.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.workers = []
        self.active_instances = 0

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Anti-Detect Browser Automation')
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel('URL:')
        url_label.setMinimumWidth(100)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://example.com')
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Proxy input
        proxy_layout = QHBoxLayout()
        proxy_label = QLabel('Proxy:')
        proxy_label.setMinimumWidth(100)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText('IP:PORT:USER:PASS (optional)')
        proxy_layout.addWidget(proxy_label)
        proxy_layout.addWidget(self.proxy_input)
        layout.addLayout(proxy_layout)

        # Instance count
        instance_layout = QHBoxLayout()
        instance_label = QLabel('Instances:')
        instance_label.setMinimumWidth(100)
        self.instance_count = QSpinBox()
        self.instance_count.setRange(1, 10)
        self.instance_count.setValue(1)
        instance_layout.addWidget(instance_label)
        instance_layout.addWidget(self.instance_count)
        instance_layout.addStretch()
        layout.addLayout(instance_layout)

        # Time range
        time_layout = QHBoxLayout()
        time_label = QLabel('Time Range (s):')
        time_label.setMinimumWidth(100)
        self.min_time = QSpinBox()
        self.min_time.setRange(5, 300)
        self.min_time.setValue(5)
        self.max_time = QSpinBox()
        self.max_time.setRange(5, 300)
        self.max_time.setValue(15)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.min_time)
        time_layout.addWidget(QLabel('to'))
        time_layout.addWidget(self.max_time)
        time_layout.addStretch()
        layout.addLayout(time_layout)

        # Start button
        self.start_button = QPushButton('Start Automation')
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_automation)
        layout.addWidget(self.start_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(200)
        layout.addWidget(self.log_area)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Ready')

        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        """Apply custom styles to the UI"""
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLabel {
            font-size: 12px;
            color: #333;
        }
        QLineEdit, QSpinBox {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: white;
        }
        QLineEdit:focus, QSpinBox:focus {
            border-color: #007bff;
        }
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QPushButton:disabled {
            background-color: #ccc;
        }
        QTextEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: white;
            font-family: monospace;
        }
        """
        self.setStyleSheet(style)

    def log_message(self, message):
        """Add message to log area"""
        self.log_area.append(message)
        # Scroll to bottom
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_error(self, message):
        """Show error message box"""
        QMessageBox.critical(self, 'Error', message)

    def update_progress(self):
        """Update progress bar"""
        self.active_instances -= 1
        progress = ((self.total_instances - self.active_instances) / self.total_instances) * 100
        self.progress_bar.setValue(int(progress))
        
        if self.active_instances == 0:
            self.automation_finished()

    def start_automation(self):
        """Start the browser automation"""
        # Validate inputs
        url = self.url_input.text().strip()
        proxy = self.proxy_input.text().strip()
        instance_count = self.instance_count.value()
        min_time = self.min_time.value()
        max_time = self.max_time.value()

        valid, error_message = validate_inputs(url, proxy, instance_count, min_time, max_time)
        if not valid:
            self.show_error(error_message)
            return

        # Disable inputs during automation
        self.start_button.setEnabled(False)
        self.url_input.setEnabled(False)
        self.proxy_input.setEnabled(False)
        self.instance_count.setEnabled(False)
        self.min_time.setEnabled(False)
        self.max_time.setEnabled(False)

        # Setup progress tracking
        self.active_instances = instance_count
        self.total_instances = instance_count
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Clear previous log
        self.log_area.clear()
        self.log_message("Starting automation...")

        # Launch browser instances
        for i in range(instance_count):
            worker = BrowserWorker(i + 1, url, proxy, min_time, max_time)
            worker.log_signal.connect(self.log_message)
            worker.error_signal.connect(self.show_error)
            worker.finished_signal.connect(self.update_progress)
            self.workers.append(worker)
            worker.start()

        self.status_bar.showMessage('Automation in progress...')

    def automation_finished(self):
        """Clean up after automation is finished"""
        # Re-enable inputs
        self.start_button.setEnabled(True)
        self.url_input.setEnabled(True)
        self.proxy_input.setEnabled(True)
        self.instance_count.setEnabled(True)
        self.min_time.setEnabled(True)
        self.max_time.setEnabled(True)

        # Clear workers
        self.workers.clear()

        # Update UI
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage('Automation completed')
        self.log_message("All instances finished.")

    def closeEvent(self, event):
        """Handle application closure"""
        # Stop all running instances
        for worker in self.workers:
            if worker.isRunning():
                worker.browser_manager.close_all_browsers()
                worker.terminate()
                worker.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()