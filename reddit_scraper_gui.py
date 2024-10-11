# File: reddit_scraper_gui.py

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox, QPushButton, 
                             QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Import your existing scraper function
from reddit_scraper import login_and_scrape_reddit, set_print_function

class ScraperWorker(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    update_log = pyqtSignal(str)
    scraping_finished = pyqtSignal(list)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            set_print_function(self.update_log.emit)
            results = login_and_scrape_reddit(**self.params)
            for i, result in enumerate(results):
                progress = int((i + 1) / len(results) * 100)
                self.update_progress.emit(progress)
                self.update_status.emit(f"Scraped post {i + 1} of {len(results)}")
            self.scraping_finished.emit(results)
        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")


class RedditScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit Scraper with AI Comments")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Input fields
        self.username = self.create_input("Username:", "bigbootyrob")
        self.password = self.create_input("Password:", "1893Apple", is_password=True)
        self.subreddit = self.create_input("Subreddit:", "AskReddit")
        
        self.sort_type = QComboBox()
        self.sort_type.addItems(["hot", "new", "top", "rising"])
        self.layout.addWidget(QLabel("Sort Type:"))
        self.layout.addWidget(self.sort_type)

        self.max_articles = self.create_spinbox("Max Articles:", 1, 100, 10)
        self.max_comments = self.create_spinbox("Max Comments per Article:", 1, 50, 10)
        
        self.pause_enabled = QCheckBox("Enable pausing between posts")
        self.layout.addWidget(self.pause_enabled)

        self.persona = QComboBox()
        self.persona.addItems(["teenager", "normal", "educated", "bot"])
        self.layout.addWidget(QLabel("AI Persona:"))
        self.layout.addWidget(self.persona)

        self.include_comments = QCheckBox("Include comments in AI prompt")
        self.include_comments.setChecked(True)
        self.layout.addWidget(self.include_comments)

        # Start button
        self.start_button = QPushButton("Start Scraping")
        self.start_button.clicked.connect(self.start_scraping)
        self.layout.addWidget(self.start_button)

        # Progress bar and status
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready to scrape")
        self.layout.addWidget(self.status_label)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.layout.addWidget(QLabel("Log:"))
        self.layout.addWidget(self.log_display)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.layout.addWidget(QLabel("Results:"))
        self.layout.addWidget(self.results_display)

    def create_input(self, label, default, is_password=False):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        input_field = QLineEdit(default)
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(input_field)
        self.layout.addLayout(layout)
        return input_field

    def create_spinbox(self, label, min_val, max_val, default):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        layout.addWidget(spinbox)
        self.layout.addLayout(layout)
        return spinbox

    def start_scraping(self):
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_display.clear()
        self.results_display.clear()

        params = {
            "username": self.username.text(),
            "password": self.password.text(),
            "subreddit": self.subreddit.text(),
            "sort_type": self.sort_type.currentText(),
            "max_articles": self.max_articles.value(),
            "max_comments": self.max_comments.value(),
            "pause_enabled": self.pause_enabled.isChecked(),
            "persona": self.persona.currentText(),
            "include_comments": self.include_comments.isChecked(),
            # Add custom headers here if needed
            "custom_headers": []  # You might want to add a way to input these in the GUI
        }

        self.worker = ScraperWorker(params)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_status.connect(self.update_status)
        self.worker.update_log.connect(self.update_log)
        self.worker.scraping_finished.connect(self.display_results)
        self.worker.start()

    def update_log(self, message):
        self.log_display.append(message)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())
        
    def update_progress(self, value):
            self.progress_bar.setValue(value)

    def update_status(self, status):
            self.status_label.setText(status)

    def display_results(self, results):
            for post in results:
                self.results_display.append(f"Title: {post['title']}")
                self.results_display.append(f"URL: {post['url']}")
                self.results_display.append(f"Number of comments: {len(post['comments'])}")
                self.results_display.append(f"AI comment: {post['ai_comment']}")
                self.results_display.append("\n")

            self.start_button.setEnabled(True)
            self.status_label.setText("Scraping completed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedditScraperGUI()
    window.show()
    sys.exit(app.exec())