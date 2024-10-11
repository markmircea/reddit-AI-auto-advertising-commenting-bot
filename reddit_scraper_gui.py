import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox, QPushButton, 
                             QTextEdit, QProgressBar, QListWidget, QMenuBar, QMenu, QDialog,
                             QDialogButtonBox, QFormLayout, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QIcon, QDesktopServices
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter, QPixmap

from reddit_scraper import login_and_scrape_reddit, set_print_function

class SVGIcon(QIcon):
    def __init__(self, svg_string, color="#D7DADC"):
        super().__init__()
        modified_svg = svg_string.replace('fill="currentColor"', f'fill="{color}"')
        renderer = QSvgRenderer(modified_svg.encode('utf-8'))
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        self.addPixmap(pixmap)

# SVG icons as strings
ICONS = {
    "file": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>''',
    "save": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>''',
    "settings": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>''',
    "license": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>''',
    "key": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path></svg>''',
    "buy": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>''',
    "add": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>''',
    "remove": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>''',
    "start": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>'''
}

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter License Key")
        self.setModal(True)

        layout = QFormLayout(self)
        self.license_key = QLineEdit(self)
        layout.addRow("License Key:", self.license_key)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class ScraperWorker(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    update_log = pyqtSignal(str)
    scraping_finished = pyqtSignal(list)

    def __init__(self, params):
        super().__init__()
        self.params = params
        self.total_comments = self.calculate_total_comments()
        self.current_comment = 0

    def calculate_total_comments(self):
        return len(self.params['subreddits']) * self.params['max_articles'] * self.params['max_comments']

    def run(self):
        try:
            set_print_function(self.custom_print)
            all_results = login_and_scrape_reddit(**self.params)
            self.scraping_finished.emit(all_results)
        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")
            print(f"Error in ScraperWorker: {str(e)}") 

    def custom_print(self, message):
        self.update_log.emit(message)
        if "Extracted comment" in message:
            self.current_comment += 1
            progress = int((self.current_comment / self.total_comments) * 100)
            self.update_progress.emit(progress)
            
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.title = QLabel("Reddit Scraper Pro")

        btn_size = 35

        self.btn_close = QPushButton("×")
        self.btn_close.clicked.connect(self.parent.close)
        self.btn_close.setFixedSize(btn_size,btn_size)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #FF4500;
                color: white;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FF5722;
            }
        """)

        self.btn_min = QPushButton("−")
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_min.setFixedSize(btn_size, btn_size)
        self.btn_min.setStyleSheet("""
            QPushButton {
                background-color: #1A1A1B;
                color: #D7DADC;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #272729;
            }
        """)

        self.title.setFixedHeight(35)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_close)

        self.start = QPoint(0, 0)
        self.pressing = False

    def resizeEvent(self, QResizeEvent):
        super(TitleBar, self).resizeEvent(QResizeEvent)
        self.title.setFixedWidth(self.parent.width())

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
                                self.mapToGlobal(self.movement).y(),
                                self.parent.width(),
                                self.parent.height())
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1A1A1B"))
        painter.drawRect(self.rect())

class RedditScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit Scraper Pro")
        self.setGeometry(100, 100, 800, 600)

        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Input fields
        self.username = self.create_input("Username:", "bigbootyrob")
        self.password = self.create_input("Password:", "1893Apple", is_password=True)
        
        # Subreddit input and list
        subreddit_layout = QHBoxLayout()
        self.subreddit_input = QLineEdit()
        self.subreddit_input.returnPressed.connect(self.add_subreddit)
        self.add_subreddit_button = QPushButton(SVGIcon(ICONS["add"]), "Add Subreddit")
        self.add_subreddit_button.clicked.connect(self.add_subreddit)
        self.remove_subreddit_button = QPushButton(SVGIcon(ICONS["remove"]), "Remove Subreddit")
        self.remove_subreddit_button.clicked.connect(self.remove_subreddit)
        subreddit_layout.addWidget(self.subreddit_input)
        subreddit_layout.addWidget(self.add_subreddit_button)
        subreddit_layout.addWidget(self.remove_subreddit_button)
        self.layout.addLayout(subreddit_layout)
        
        self.subreddit_list = QListWidget()
        self.subreddit_list.addItem("AskReddit")  # Default entry
        self.layout.addWidget(self.subreddit_list)
        
        self.sort_type = QComboBox()
        self.sort_type.addItems(["hot", "new", "top", "rising"])
        self.layout.addWidget(QLabel("Sort Type:"))
        self.layout.addWidget(self.sort_type)

        self.max_articles = self.create_spinbox("Max Articles per Subreddit:", 1, 100, 10)
        self.max_comments = self.create_spinbox("Max Comments per Article:", 1, 50, 10)
        
        # Added new input fields for random wait time
        wait_time_layout = QHBoxLayout()
        wait_time_layout.addWidget(QLabel("Wait time before posting - in (seconds):"))
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

        self.persona = QComboBox()
        self.persona.addItems(["teenager", "normal", "educated", "bot"])
        self.layout.addWidget(QLabel("AI Persona:"))
        self.layout.addWidget(self.persona)
        
        # AI response length
        self.ai_response_length = self.create_spinbox("AI Response Length (words, 0 for default):", 0, 1000, 0)

        self.include_comments = QCheckBox("Include comments in AI prompt")
        self.include_comments.setChecked(True)
        self.layout.addWidget(self.include_comments)

        self.include_comments = QCheckBox("Include comments in AI prompt")
        self.include_comments.setChecked(True)
        self.layout.addWidget(self.include_comments)

        # Start button
        self.start_button = QPushButton(SVGIcon(ICONS["start"]), "Start Scraping")
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

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A1B;
                color: #D7DADC;
            }
            QMenuBar {
                background-color: #1A1A1B;
                color: #D7DADC;
                border-bottom: 1px solid #343536;
            }
            QMenuBar::item:selected {
                background-color: #272729;
            }
            QMenu {
                background-color: #1A1A1B;
                color: #D7DADC;
                border: 1px solid #343536;
            }
            QMenu::item:selected {
                background-color: #272729;
            }
            QLabel, QCheckBox, QRadioButton {
                color: #D7DADC;
            }
            QPushButton {
                background-color: #FF4500;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #FF5722;
            }
            QLineEdit, QTextEdit, QListWidget, QComboBox, QSpinBox {
                background-color: #272729;
                color: #D7DADC;
                border: 1px solid #343536;
                border-radius: 3px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #343536;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #FF4500;
            }
            QScrollBar:vertical {
                border: none;
                background: #272729;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #4A4A4D;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu(SVGIcon(ICONS["file"]), "&File")
        save_action = QAction(SVGIcon(ICONS["save"]), "Save Results", self)
        save_action.triggered.connect(self.save_results)
        file_menu.addAction(save_action)

        # Settings menu
        settings_menu = menu_bar.addMenu(SVGIcon(ICONS["settings"]), "&Settings")
        proxy_action = QAction(SVGIcon(ICONS["settings"]), "Proxy Settings", self)
        proxy_action.triggered.connect(self.open_proxy_settings)
        settings_menu.addAction(proxy_action)

        # License menu
        license_menu = menu_bar.addMenu(SVGIcon(ICONS["license"]), "&License")
        enter_key_action = QAction(SVGIcon(ICONS["key"]), "Enter License Key", self)
        enter_key_action.triggered.connect(self.enter_license_key)
        license_menu.addAction(enter_key_action)
        buy_license_action = QAction(SVGIcon(ICONS["buy"]), "Buy License", self)
        buy_license_action.triggered.connect(self.buy_license)
        license_menu.addAction(buy_license_action)

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
            "persona": self.persona.currentText(),
            "include_comments": self.include_comments.isChecked(),
            "custom_headers": [],
            "ai_response_length": self.ai_response_length.value()  # Add this line
        }


        self.worker = ScraperWorker(params)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_status.connect(self.update_status)
        self.worker.update_log.connect(self.update_log)
        self.worker.scraping_finished.connect(self.display_results)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def update_log(self, message):
        self.log_display.append(message)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())

    def display_results(self, results):
        for post in results:
            self.results_display.append(f"Subreddit: r/{post['subreddit']}")
            self.results_display.append(f"Title: {post['title']}")
            self.results_display.append(f"URL: {post['url']}")
            self.results_display.append(f"Number of comments: {len(post['comments'])}")
            self.results_display.append(f"AI comment: {post['ai_comment']}")
            self.results_display.append("\n")

        self.start_button.setEnabled(True)
        self.status_label.setText("Scraping completed")

    def save_results(self):
        # Implement save functionality
        QMessageBox.information(self, "Save Results", "Save functionality not implemented yet.")

    def open_proxy_settings(self):
        # Implement proxy settings dialog
        QMessageBox.information(self, "Proxy Settings", "Proxy settings functionality not implemented yet.")

    def enter_license_key(self):
        dialog = LicenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            license_key = dialog.license_key.text()
            # Here you would validate the license key
            QMessageBox.information(self, "License Key", "License key entered: " + license_key)

    def buy_license(self):
        # Open the license purchase website
        QDesktopServices.openUrl(QUrl("https://your-license-purchase-url.com"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedditScraperGUI()
    window.show()
    sys.exit(app.exec())