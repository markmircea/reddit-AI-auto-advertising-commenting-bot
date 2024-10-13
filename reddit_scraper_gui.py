import sys
import json
import os
import random
import time
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox, QPushButton, 
                             QTextEdit, QProgressBar, QListWidget, QMenuBar, QMenu, QMessageBox, 
                             QFileDialog, QFrame, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QPoint
from PyQt6.QtGui import QAction, QDesktopServices

from gui_components import (SVGIcon, LicenseDialog, ProxySettingsDialog, BrowserFingerprintDialog, 
                            AdvancedSettingsDialog, CommentReviewDialog)
from scraper import login_and_scrape_reddit, set_print_function, post_comment
from utils import ICONS, write_to_log_file, clear_log_file, save_settings, load_settings, export_text
from styles import apply_dark_theme, style_save_button, style_advanced_settings_button, style_start_button

class ScraperWorker(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    update_log = pyqtSignal(str)
    scraping_finished = pyqtSignal(list, object)

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.total_comments = self.calculate_total_comments()
        self.current_comment = 0
        self.driver = None
        
    def calculate_total_comments(self):
        return len(self.params['subreddits']) * self.params['max_articles'] * self.params['max_comments']

    def run(self):
        try:
            set_print_function(self.custom_print)
            self.update_log.emit("Starting the scraping process...")
            all_results, self.driver = login_and_scrape_reddit(**self.params)
            self.update_log.emit("Scraping process completed.")
            self.scraping_finished.emit(all_results, self.driver)
        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")
            self.update_log.emit(f"Error in ScraperWorker: {str(e)}")
            print(f"Error in ScraperWorker: {str(e)}")

    def custom_print(self, message):
        self.update_log.emit(message)
        write_to_log_file(message)
        if "Extracted comment" in message:
            self.current_comment += 1
            progress = int((self.current_comment / self.total_comments) * 100)
            self.update_progress.emit(progress)

class RedditScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit AI Commenter Pro")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(100, 100, 800, screen_geometry.height())

        self.create_menu_bar()
        self.proxy_settings = {}
        self.fingerprint_settings = {}
        self.advanced_settings = {
            "openrouter_api_key": "",
            "scroll_retries": 2,
            "button_retries": 2,
            "persona": "normal",
            "custom_model": "google/gemma-2-9b-it:free",
            "product_keywords": "",
            "similarity_threshold": 0.5,
        }

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        self.create_ui_elements()
        self.apply_styles()
        self.load_settings_if_exists()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(SVGIcon(ICONS["file"]), "&File")
        save_settings_action = QAction(SVGIcon(ICONS["save"]), "Save Settings", self)
        save_settings_action.triggered.connect(self.save_settings)
        file_menu.addAction(save_settings_action)

        import_settings_action = QAction(SVGIcon(ICONS["file"]), "Import Settings", self)
        import_settings_action.triggered.connect(self.import_settings)
        file_menu.addAction(import_settings_action)

        export_log_action = QAction(SVGIcon(ICONS["file"]), "Export Log", self)
        export_log_action.triggered.connect(self.export_log)
        file_menu.addAction(export_log_action)

        export_results_action = QAction(SVGIcon(ICONS["file"]), "Export Results", self)
        export_results_action.triggered.connect(self.export_results)
        file_menu.addAction(export_results_action)

        settings_menu = menu_bar.addMenu(SVGIcon(ICONS["settings"]), "&Settings")
        proxy_action = QAction(SVGIcon(ICONS["settings"]), "Proxy Settings", self)
        proxy_action.triggered.connect(self.open_proxy_settings)
        settings_menu.addAction(proxy_action)
        
        fingerprint_action = QAction(SVGIcon(ICONS["settings"]), "Browser Fingerprint Settings", self)
        fingerprint_action.triggered.connect(self.open_fingerprint_settings)
        settings_menu.addAction(fingerprint_action)
        
        advanced_settings_action = QAction(SVGIcon(ICONS["settings"]), "Advanced Settings", self)
        advanced_settings_action.triggered.connect(self.open_advanced_settings)
        settings_menu.addAction(advanced_settings_action)
        
        license_menu = menu_bar.addMenu(SVGIcon(ICONS["license"]), "&License")
        enter_key_action = QAction(SVGIcon(ICONS["key"]), "Enter License Key", self)
        enter_key_action.triggered.connect(self.enter_license_key)
        license_menu.addAction(enter_key_action)
        buy_license_action = QAction(SVGIcon(ICONS["buy"]), "Buy License", self)
        buy_license_action.triggered.connect(self.buy_license)
        license_menu.addAction(buy_license_action)

    def create_ui_elements(self):
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(SVGIcon(ICONS["save"]), "Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        self.advanced_settings_button = QPushButton(SVGIcon(ICONS["settings"]), "Advanced Settings")
        self.advanced_settings_button.clicked.connect(self.open_advanced_settings)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.advanced_settings_button)
        self.layout.addLayout(button_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(separator)

        self.username = self.create_input("Username:", "bigbootyrob")
        self.password = self.create_input("Password:", "1893Apple", is_password=True)

        subreddit_layout = QHBoxLayout()
        self.subreddit_input = QLineEdit()
        self.subreddit_input.setPlaceholderText("Enter subreddit name")
        self.subreddit_input.returnPressed.connect(self.add_subreddit)
        self.add_subreddit_button = QPushButton(SVGIcon(ICONS["add"]), "Add")
        self.add_subreddit_button.clicked.connect(self.add_subreddit)
        self.remove_subreddit_button = QPushButton(SVGIcon(ICONS["remove"]), "Remove")
        self.remove_subreddit_button.clicked.connect(self.remove_subreddit)
        subreddit_layout.addWidget(self.subreddit_input)
        subreddit_layout.addWidget(self.add_subreddit_button)
        subreddit_layout.addWidget(self.remove_subreddit_button)
        self.layout.addLayout(subreddit_layout)
        
        self.subreddit_list = QListWidget()
        self.subreddit_list.addItem("AskReddit")
        self.subreddit_list.setMaximumHeight(100)
        self.layout.addWidget(self.subreddit_list)
        
        self.sort_type = QComboBox()
        self.sort_type.addItems(["hot", "new", "top", "rising"])
        self.layout.addWidget(QLabel("Sort Type:"))
        self.layout.addWidget(self.sort_type)

        self.max_articles = self.create_spinbox("Max Articles per Subreddit:", 1, 1000, 10)
        self.max_comments = self.create_spinbox("Max Comments per Article:", 0, 1000, 10)

        wait_time_layout = QHBoxLayout()
        wait_time_layout.addWidget(QLabel("Wait time before posting (seconds):"))
        self.min_wait_time = QSpinBox()
        self.min_wait_time.setRange(0, 3600)
        self.min_wait_time.setValue(4)
        wait_time_layout.addWidget(self.min_wait_time)
        wait_time_layout.addWidget(QLabel("to"))
        self.max_wait_time = QSpinBox()
        self.max_wait_time.setRange(0, 3600)
        self.max_wait_time.setValue(6)
        wait_time_layout.addWidget(self.max_wait_time)
        self.layout.addLayout(wait_time_layout)

        self.ai_response_length = self.create_spinbox("AI Response Length (words, 0 for auto):", 0, 1000, 0)

        self.do_not_post = QCheckBox("Generate AI comments only (do not review)")
        self.layout.addWidget(self.do_not_post)

        self.start_button = QPushButton(SVGIcon(ICONS["start"]), "Start Scraping, Generating and Reviewing Comments")
        self.start_button.clicked.connect(self.start_scraping)
        self.layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready to scrape")
        self.layout.addWidget(self.status_label)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.layout.addWidget(QLabel("Log:"))
        self.layout.addWidget(self.log_display)
        self.log_display.setMinimumHeight(300)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.layout.addWidget(QLabel("Results:"))
        self.layout.addWidget(self.results_display)

    def apply_styles(self):
        apply_dark_theme(self)
        style_save_button(self.save_button)
        style_advanced_settings_button(self.advanced_settings_button)
        style_start_button(self.start_button)

    def save_settings(self, default_filename="settings.json"):
        settings = {
            "username": self.username.text(),
            "password": self.password.text(),
            "subreddits": [self.subreddit_list.item(i).text() for i in range(self.subreddit_list.count())],
            "sort_type": self.sort_type.currentText(),
            "max_articles": self.max_articles.value(),
            "max_comments": self.max_comments.value(),
            "min_wait_time": self.min_wait_time.value(),
            "max_wait_time": self.max_wait_time.value(),
            "ai_response_length": self.ai_response_length.value(),
            "proxy_settings": self.proxy_settings,
            "fingerprint_settings": self.fingerprint_settings,
            "advanced_settings": self.advanced_settings,
        }

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Settings", default_filename, "JSON Files (*.json)")
        if file_name:
            save_settings(settings, file_name)
            self.update_status(f"Settings saved to {file_name}")
            
    def import_settings(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Settings", "settings.json", "JSON Files (*.json)")
        if file_name:
            self.load_settings(file_name)

    def load_settings(self, file_name):
        try:
            settings = load_settings(file_name)

            self.username.setText(settings.get("username", ""))
            self.password.setText(settings.get("password", ""))
            self.subreddit_list.clear()
            self.subreddit_list.addItems(settings.get("subreddits", []))
            self.sort_type.setCurrentText(settings.get("sort_type", "hot"))
            self.max_articles.setValue(settings.get("max_articles", 10))
            self.max_comments.setValue(settings.get("max_comments", 10))
            self.min_wait_time.setValue(settings.get("min_wait_time", 4))
            self.max_wait_time.setValue(settings.get("max_wait_time", 6))
            self.ai_response_length.setValue(settings.get("ai_response_length", 0))
            self.proxy_settings = settings.get("proxy_settings", {})
            self.fingerprint_settings = settings.get("fingerprint_settings", {})
            self.advanced_settings = settings.get("advanced_settings", self.advanced_settings)
            self.update_status(f"Settings imported from {file_name}")
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Failed to import settings: {str(e)}")

    def load_settings_if_exists(self):
        if os.path.exists("settings.json"):
            self.load_settings("settings.json")

    def export_log(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Log", "", "Text Files (*.txt)")
        if file_name:
            try:
                export_text(self.log_display.toPlainText(), file_name)
                self.update_status(f"Log exported to {file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export log: {str(e)}")

    def export_results(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Results", "", "Text Files (*.txt)")
        if file_name:
            export_text(self.results_display.toPlainText(), file_name)
            self.update_status(f"Results exported to {file_name}")

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

    def add_subreddit(self):
        subreddit = self.subreddit_input.text().strip()
        if subreddit and subreddit not in [self.subreddit_list.item(i).text() for i in range(self.subreddit_list.count())]:
            self.subreddit_list.addItem(subreddit)
            self.subreddit_input.clear()

    def remove_subreddit(self):
        current_item = self.subreddit_list.currentItem()
        if current_item:
            row = self.subreddit_list.row(current_item)
            self.subreddit_list.takeItem(row)

    def start_scraping(self):
        clear_log_file()
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_display.clear()
        self.results_display.clear()

        subreddits = [self.subreddit_list.item(i).text() for i in range(self.subreddit_list.count())]
        if not subreddits:
            self.update_status("Please add at least one subreddit before starting.")
            self.start_button.setEnabled(True)
            return

        params = {
            "username": self.username.text(),
            "password": self.password.text(),
            "subreddits": subreddits,
            "sort_type": self.sort_type.currentText(),
            "max_articles": self.max_articles.value(),
            "max_comments": self.max_comments.value(),
            "min_wait_time": self.min_wait_time.value(),
            "max_wait_time": self.max_wait_time.value(),
            "custom_headers": [],
            "ai_response_length": self.ai_response_length.value(),
            "proxy_settings": self.proxy_settings,
            "fingerprint_settings": self.fingerprint_settings,
            "do_not_post": self.do_not_post.isChecked(),
            "openrouter_api_key": self.advanced_settings.get("openrouter_api_key", "").strip(),
            "custom_prompt": self.advanced_settings.get("custom_prompt", "").strip(),
            "product_keywords": self.advanced_settings.get("product_keywords", ""),
            "similarity_threshold": self.advanced_settings.get("similarity_threshold", 0.5),
            "similarity_method": self.advanced_settings.get("similarity_method", "TensorFlow (semantic_similarity)"),
            **self.advanced_settings
        }

        self.worker = ScraperWorker(params)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_status.connect(self.update_status)
        self.worker.update_log.connect(self.update_log)
        self.worker.scraping_finished.connect(self.handle_scraping_finished)
        self.worker.start()
        
    def handle_scraping_finished(self, results, driver):
        self.update_log("Scraping process finished. Handling results...")
        self.driver = driver
        if self.do_not_post.isChecked():
            self.update_log("Skipping Review...")
            self.display_results(results)
        else:
            self.update_log("Review mode is active. Opening comment review dialog...")
            dialog = CommentReviewDialog(results, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_comments = dialog.get_selected_comments()
                self.update_log(f"User selected {len(selected_comments)} comments for posting.")
                self.post_selected_comments(selected_comments)
            else:
                self.update_log("User cancelled comment review.")
            
        self.display_results(results)
        self.start_button.setEnabled(True)
        self.status_label.setText("Scraping completed")

    def post_selected_comments(self, selected_comments):
        self.update_log(f"Preparing to post {len(selected_comments)} comments...")
        for comment in selected_comments:
            wait_time = random.uniform(self.min_wait_time.value(), self.max_wait_time.value())
            self.update_log(f"Waiting {wait_time:.2f} seconds before posting comment...")
            time.sleep(wait_time)
        
            self.update_log(f"Posting comment for '{comment['title']}' in r/{comment['subreddit']}...")
            self.update_log(f"Comment URL: {comment['url']}")
            self.update_log(f"AI Comment: {comment['ai_comment'][:100]}...")
        
            success = post_comment(self.driver, comment['ai_comment'], comment['url'])
        
            if success:
                self.update_log(f"Successfully posted comment in r/{comment['subreddit']}")
            else:
                self.update_log(f"Failed to post comment in r/{comment['subreddit']}")
        
            QApplication.processEvents()

        self.update_status("Finished posting selected comments")
        self.update_log("All selected comments have been processed.")
        self.driver.quit()

    def update_log(self, message):
        write_to_log_file(message)
        self.log_display.append(message)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())
        QApplication.processEvents()
            
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def display_results(self, results):
        self.results_display.clear()
        for post in results:
            self.results_display.append(f"Subreddit: r/{post['subreddit']}")
            self.results_display.append(f"Title: {post['title']}")
            self.results_display.append(f"URL: {post['url']}")
            if 'comments' in post:
                self.results_display.append(f"Number of comments: {len(post['comments'])}")
            self.results_display.append(f"AI comment: {post['ai_comment'][:100]}...")
            self.results_display.append("\n")

        self.results_display.append(f"Total posts scraped: {len(results)}")
        self.start_button.setEnabled(True)
        self.status_label.setText("Scraping completed")

    def open_proxy_settings(self):
        dialog = ProxySettingsDialog(self)
        dialog.set_proxy_settings(self.proxy_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.proxy_settings = dialog.get_proxy_settings()
            self.update_status("Proxy settings updated")

    def open_fingerprint_settings(self):
        dialog = BrowserFingerprintDialog(self)
        dialog.set_fingerprint_settings(self.fingerprint_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.fingerprint_settings = dialog.get_fingerprint_settings()
            self.update_status("Browser fingerprint settings updated")

    def open_advanced_settings(self):
        dialog = AdvancedSettingsDialog(self)
        dialog.set_settings(self.advanced_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.advanced_settings = dialog.get_settings()
            self.update_status("Advanced settings updated")

    def enter_license_key(self):
        dialog = LicenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            license_key = dialog.license_key.text()
            QMessageBox.information(self, "License Key", "License key entered: " + license_key)

    def buy_license(self):
        QDesktopServices.openUrl(QUrl("https://your-license-purchase-url.com"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedditScraperGUI()
    window.show()
    sys.exit(app.exec())
