import sys
import json
import os
import random
import time
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox, QPushButton, 
                             QTextEdit, QProgressBar, QListWidget, QMenuBar, QMenu, QDialog,
                             QDialogButtonBox, QFormLayout, QMessageBox, QFrame, QFileDialog, QPlainTextEdit, QGroupBox, QInputDialog, QTableWidget, QTableWidgetItem, QHeaderView,
                             QStyledItemDelegate, QStyleOptionViewItem, QStyle)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QPoint, QSize
from PyQt6.QtGui import QAction, QIcon, QDesktopServices, QPainter, QPixmap, QColor, QTextDocument, QAbstractTextDocumentLayout
from PyQt6.QtSvg import QSvgRenderer

from reddit_scraper import login_and_scrape_reddit, set_print_function, post_comment

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

class HTMLDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        style = option.widget.style() if option.widget else QApplication.style()

        doc = QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        
        doc = QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        
        return QSize(int(doc.idealWidth()), int(doc.size().height()))

class CommentReviewDialog(QDialog):
    def __init__(self, comments, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review AI Generated Comments")
        self.setGeometry(100, 100, 1200, 800)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Post", "Subreddit", "AI Comment", "Edit", "Keep"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setItemDelegateForColumn(2, HTMLDelegate())

        for i, comment in enumerate(comments):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(comment['title']))
            self.table.setItem(i, 1, QTableWidgetItem(comment['subreddit']))
            
            full_comment = comment['ai_comment'].replace('\n', '<br>')
            comment_item = QTableWidgetItem(full_comment)
            comment_item.setData(Qt.ItemDataRole.UserRole, comment['url'])  # Store URL in user role
            self.table.setItem(i, 2, comment_item)

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda _, row=i: self.edit_comment(row))
            self.table.setCellWidget(i, 3, edit_button)

            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            checkbox.setCheckState(Qt.CheckState.Checked)
            self.table.setItem(i, 4, checkbox)

        self.table.resizeRowsToContents()
        layout.addWidget(self.table)

        self.send_button = QPushButton("Send Selected Comments")
        self.send_button.clicked.connect(self.accept)
        layout.addWidget(self.send_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

    def edit_comment(self, row):
        current_comment = self.table.item(row, 2).text()
        current_comment = current_comment.replace('<br>', '\n').replace('<p style=\'white-space: pre-wrap;\'>', '').replace('</p>', '')
        dialog = CommentEditDialog(current_comment, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_comment = dialog.comment_edit.toPlainText()
            new_comment_html = "<p style='white-space: pre-wrap;'>{}</p>".format(new_comment.replace('\n', '<br>'))
            self.table.setItem(row, 2, QTableWidgetItem(new_comment_html))
            self.table.resizeRowToContents(row)

    def get_selected_comments(self):
        selected_comments = []
        for i in range(self.table.rowCount()):
            if self.table.item(i, 4).checkState() == Qt.CheckState.Checked:
                comment_html = self.table.item(i, 2).text()
                comment_text = comment_html.replace('<br>', '\n').replace('<p style=\'white-space: pre-wrap;\'>', '').replace('</p>', '')
                comment = {
                    'title': self.table.item(i, 0).text(),
                    'subreddit': self.table.item(i, 1).text(),
                    'ai_comment': comment_text,
                    'url': self.table.item(i, 2).data(Qt.ItemDataRole.UserRole)  # Retrieve URL from user role
                }
                selected_comments.append(comment)
        return selected_comments

class CommentEditDialog(QDialog):
    def __init__(self, comment, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Comment")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout(self)

        self.comment_edit = QPlainTextEdit(self)
        self.comment_edit.setPlainText(comment)
        layout.addWidget(self.comment_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
    scraping_finished = pyqtSignal(list, object)  # Changed to pass driver object

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
            all_results, self.driver = login_and_scrape_reddit(
                username=self.params['username'],
                password=self.params['password'],
                subreddits=self.params['subreddits'],
                sort_type=self.params['sort_type'],
                max_articles=self.params['max_articles'],
                max_comments=self.params['max_comments'],
                min_wait_time=self.params['min_wait_time'],
                max_wait_time=self.params['max_wait_time'],
                custom_headers=self.params['custom_headers'],
                ai_response_length=self.params['ai_response_length'],
                proxy_settings=self.params['proxy_settings'],
                fingerprint_settings=self.params['fingerprint_settings'],
                do_not_post=self.params['do_not_post'],
                openrouter_api_key=self.params['openrouter_api_key'],
                scroll_retries=self.params['scroll_retries'],
                button_retries=self.params['button_retries'],
                persona=self.params['persona'],
                custom_model=self.params['custom_model'],
                custom_prompt=self.params['custom_prompt'],
                product_description=self.params['product_description'],
                website_address=self.params['website_address']
            )
            self.update_log.emit("Scraping process completed.")
            self.scraping_finished.emit(all_results, self.driver)
        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")
            self.update_log.emit(f"Error in ScraperWorker: {str(e)}")
            print(f"Error in ScraperWorker: {str(e)}")
    def custom_print(self, message):
        self.update_log.emit(message)
        if "Extracted comment" in message:
            self.current_comment += 1
            progress = int((self.current_comment / self.total_comments) * 100)
            self.update_progress.emit(progress)
            
class ProxySettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Proxy Settings")
        self.setModal(True)

        layout = QFormLayout(self)

        self.proxy_enabled = QCheckBox("Enable Proxy")
        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        self.proxy_host = QLineEdit()
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_username = QLineEdit()
        self.proxy_password = QLineEdit()
        self.proxy_password.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Enable Proxy:", self.proxy_enabled)
        layout.addRow("Proxy Type:", self.proxy_type)
        layout.addRow("Proxy Host:", self.proxy_host)
        layout.addRow("Proxy Port:", self.proxy_port)
        layout.addRow("Username:", self.proxy_username)
        layout.addRow("Password:", self.proxy_password)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_proxy_settings(self):
        return {
            "enabled": self.proxy_enabled.isChecked(),
            "type": self.proxy_type.currentText(),
            "host": self.proxy_host.text(),
            "port": self.proxy_port.value(),
            "username": self.proxy_username.text(),
            "password": self.proxy_password.text()
        }

    def set_proxy_settings(self, settings):
        self.proxy_enabled.setChecked(settings.get("enabled", False))
        self.proxy_type.setCurrentText(settings.get("type", "HTTP"))
        self.proxy_host.setText(settings.get("host", ""))
        self.proxy_port.setValue(settings.get("port", 8080))
        self.proxy_username.setText(settings.get("username", ""))
        self.proxy_password.setText(settings.get("password", ""))            

class BrowserFingerprintDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser Fingerprint Settings")
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.enable_fingerprinting = QCheckBox("Enable Custom Fingerprinting")
        layout.addWidget(self.enable_fingerprinting)

        form_layout = QFormLayout()

        # User Agent
        self.user_agent_input = QLineEdit()
        form_layout.addRow("User Agent:", self.user_agent_input)

        # Platform
        self.platform_input = QLineEdit()
        form_layout.addRow("Platform:", self.platform_input)

        # Screen Resolution
        resolution_layout = QHBoxLayout()
        self.screen_width = QSpinBox()
        self.screen_width.setRange(800, 3840)
        self.screen_height = QSpinBox()
        self.screen_height.setRange(600, 2160)
        resolution_layout.addWidget(self.screen_width)
        resolution_layout.addWidget(QLabel("x"))
        resolution_layout.addWidget(self.screen_height)
        form_layout.addRow("Screen Resolution:", resolution_layout)

        layout.addLayout(form_layout)

        self.randomize_button = QPushButton("Randomize Settings")
        self.randomize_button.clicked.connect(self.randomize_settings)
        layout.addWidget(self.randomize_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #E0E0E0;
            }
            QLabel, QCheckBox {
                color: #E0E0E0;
            }
            QLineEdit, QSpinBox {
                background-color: #2A2A2A;
                color: #E0E0E0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #1DB954;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
            QPushButton:pressed {
                background-color: #1AA34A;
            }
        """)

    def randomize_settings(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        platforms = ["Windows", "MacIntel", "Linux x86_64"]
        
        self.user_agent_input.setText(random.choice(user_agents))
        self.platform_input.setText(random.choice(platforms))
        self.screen_width.setValue(random.choice([1366, 1920, 2560]))
        self.screen_height.setValue(random.choice([768, 1080, 1440]))

    def get_fingerprint_settings(self):
        return {
            "enabled": self.enable_fingerprinting.isChecked(),
            "userAgent": self.user_agent_input.text(),
            "platform": self.platform_input.text(),
            "screen.width": str(self.screen_width.value()),
            "screen.height": str(self.screen_height.value())
        }

    def set_fingerprint_settings(self, settings):
        self.enable_fingerprinting.setChecked(settings.get("enabled", False))
        self.user_agent_input.setText(settings.get("userAgent", ""))
        self.platform_input.setText(settings.get("platform", ""))
        self.screen_width.setValue(int(settings.get("screen.width", 1920)))
        self.screen_height.setValue(int(settings.get("screen.height", 1080)))
        
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
        
class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)  # Increased height to accommodate new fields

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.openrouter_api_key = QLineEdit(self)
        self.openrouter_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("OpenRouter API Key:", self.openrouter_api_key)

        self.scroll_retries = QSpinBox(self)
        self.scroll_retries.setRange(0, 20)
        form_layout.addRow("Comment Scroll Retry Attempts:", self.scroll_retries)

        self.button_retries = QSpinBox(self)
        self.button_retries.setRange(0, 20)
        form_layout.addRow("Comment 'View More' Button Retry Attempts:", self.button_retries)

        self.persona = QComboBox(self)
        self.persona.addItems(["normal", "teenager", "educated", "bot"])
        form_layout.addRow("AI Persona:", self.persona)

        self.custom_model = QLineEdit(self)
        self.custom_model.setPlaceholderText("e.g., google/gemma-2-9b-it:free")
        form_layout.addRow("Custom OpenRouter Model:", self.custom_model)

        # New fields for product description and website address
        self.product_description = QLineEdit(self)
        self.product_description.setPlaceholderText("Enter product keywords")
        form_layout.addRow("Product Description:", self.product_description)

        self.website_address = QLineEdit(self)
        self.website_address.setPlaceholderText("Enter website URL")
        form_layout.addRow("Website Address:", self.website_address)

        layout.addLayout(form_layout)

        # Custom prompt input
        prompt_label = QLabel("Custom AI Prompt:")
        self.custom_prompt = QTextEdit(self)
        self.custom_prompt.setPlaceholderText("Enter your custom prompt here. Use {title}, {length}, {product}, and {website} as placeholders. ex: I want you to generate an useful comment based on the {title} of this reddit post that incorporates my {website}. My {website} is about {product}. {length}")
        self.custom_prompt.setMinimumHeight(100)
        layout.addWidget(prompt_label)
        layout.addWidget(self.custom_prompt)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        return {
            "openrouter_api_key": self.openrouter_api_key.text(),
            "scroll_retries": self.scroll_retries.value(),
            "button_retries": self.button_retries.value(),
            "persona": self.persona.currentText(),
            "custom_model": self.custom_model.text(),
            "custom_prompt": self.custom_prompt.toPlainText(),
            "product_description": self.product_description.text(),
            "website_address": self.website_address.text()
        }

    def set_settings(self, settings):
        self.openrouter_api_key.setText(settings.get("openrouter_api_key", ""))
        self.scroll_retries.setValue(settings.get("scroll_retries", 2))
        self.button_retries.setValue(settings.get("button_retries", 2))
        self.persona.setCurrentText(settings.get("persona", "normal"))
        self.custom_model.setText(settings.get("custom_model", ""))
        self.custom_prompt.setPlainText(settings.get("custom_prompt", ""))
        self.product_description.setText(settings.get("product_description", ""))
        self.website_address.setText(settings.get("website_address", ""))

class RedditScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit AI Commenter Pro")
        self.setGeometry(100, 100, 800, 600)

        self.create_menu_bar()
        self.proxy_settings = {}
        self.fingerprint_settings = {}
        self.advanced_settings = {
            "openrouter_api_key": "",
            "scroll_retries": 2,
            "button_retries": 2,
            "persona": "normal",
            "custom_model": "google/gemma-2-9b-it:free"
        }

        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        # Add Save and Advanced Settings buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(SVGIcon(ICONS["save"]), "Save Settings")
        self.save_button.clicked.connect(self.save_settings_button_clicked)  # Change this line

        self.advanced_settings_button = QPushButton(SVGIcon(ICONS["settings"]), "Advanced Settings")
        self.advanced_settings_button.clicked.connect(self.open_advanced_settings)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.advanced_settings_button)
        self.layout.addLayout(button_layout)

        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(separator)

        # Input fields
        self.username = self.create_input("Username:", "bigbootyrob")
        self.password = self.create_input("Password:", "1893Apple", is_password=True)

        # Subreddit input and list
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
        self.subreddit_list.addItem("AskReddit")  # Default entry
        self.layout.addWidget(self.subreddit_list)
        
        self.sort_type = QComboBox()
        self.sort_type.addItems(["hot", "new", "top", "rising"])
        self.layout.addWidget(QLabel("Sort Type:"))
        self.layout.addWidget(self.sort_type)

        self.max_articles = self.create_spinbox("Max Articles per Subreddit:", 1, 1000, 10)
        self.max_comments = self.create_spinbox("Max Comments per Article:", 0, 1000, 10)        
        # New input fields for retry attempts
        
        # Wait time input fields
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

        
        
        # AI response length
        self.ai_response_length = self.create_spinbox("AI Response Length (words, 0 for auto):", 0, 1000, 0)

         

        # New checkbox for not posting comments
        self.do_not_post = QCheckBox("Generate AI comments only (do not post)")
        self.layout.addWidget(self.do_not_post)

        # Start button
        self.start_button = QPushButton(SVGIcon(ICONS["start"]), "Start Scraping, Generating and Posting Comments")
        self.start_button.clicked.connect(self.start_scraping)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
            QPushButton:pressed {
                background-color: #1AA34A;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
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
        
        self.load_settings_if_exists()
        
    def save_settings_button_clicked(self):
        self.save_settings()

    def apply_styles(self):
        # Add specific styles for the new buttons
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        self.advanced_settings_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007B9E;
            }
            QPushButton:pressed {
                background-color: #006A87;
            }
        """)
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #121212;
                color: #E0E0E0;
            }
            QMenuBar {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border-bottom: 1px solid #333333;
            }
            QMenuBar::item:selected {
                background-color: #2A2A2A;
            }
            QMenu {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #333333;
            }
            QMenu::item:selected {
                background-color: #2A2A2A;
            }
            QLabel, QCheckBox, QRadioButton {
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #1DB954;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
            QPushButton:pressed {
                background-color: #1AA34A;
            }
            QLineEdit, QTextEdit, QListWidget, QComboBox, QSpinBox {
                background-color: #2A2A2A;
                color: #E0E0E0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #1DB954;
                border-radius: 3px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2A2A2A;
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
    
    def open_proxy_settings(self):
        dialog = ProxySettingsDialog(self)
        dialog.set_proxy_settings(self.proxy_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.proxy_settings = dialog.get_proxy_settings()
            self.update_status("Proxy settings updated")
            
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu(SVGIcon(ICONS["file"]), "&File")
        
        save_settings_action = QAction(SVGIcon(ICONS["save"]), "Save Settings", self)
        save_settings_action.triggered.connect(lambda: self.save_settings("settings.json"))
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

        # Settings menu
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
        
        # License menu
        license_menu = menu_bar.addMenu(SVGIcon(ICONS["license"]), "&License")
        enter_key_action = QAction(SVGIcon(ICONS["key"]), "Enter License Key", self)
        enter_key_action.triggered.connect(self.enter_license_key)
        license_menu.addAction(enter_key_action)
        buy_license_action = QAction(SVGIcon(ICONS["buy"]), "Buy License", self)
        buy_license_action.triggered.connect(self.buy_license)
        license_menu.addAction(buy_license_action)
        
    def open_advanced_settings(self):
        dialog = AdvancedSettingsDialog(self)
        dialog.set_settings(self.advanced_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.advanced_settings = dialog.get_settings()
            self.update_status("Advanced settings updated")
            
    def open_fingerprint_settings(self):
        dialog = BrowserFingerprintDialog(self)
        dialog.set_fingerprint_settings(self.fingerprint_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.fingerprint_settings = dialog.get_fingerprint_settings()
            self.update_status("Browser fingerprint settings updated")

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
            with open(file_name, 'w') as f:
                json.dump(settings, f, indent=4)
            self.update_status(f"Settings saved to {file_name}")
            
    def import_settings(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Settings", "settings.json", "JSON Files (*.json)")
        if file_name:
            self.load_settings(file_name)

    def load_settings(self, file_name):
        try:
            with open(file_name, 'r') as f:
                settings = json.load(f)

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
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                self.update_status(f"Log exported to {file_name}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export log: {str(e)}")

    def export_results(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Results", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.results_display.toPlainText())
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
      
            **self.advanced_settings  # Include advanced settings
        }

        self.worker = ScraperWorker(params)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_status.connect(self.update_status)
        self.worker.update_log.connect(self.update_log)
        self.worker.scraping_finished.connect(self.handle_scraping_finished)
        self.worker.start()
        
    def handle_scraping_finished(self, results, driver):
        self.update_log("Scraping process finished. Handling results...")
        self.driver = driver  # Store the driver object
        if self.do_not_post.isChecked():
            self.update_log("Review mode is active. Opening comment review dialog...")
            dialog = CommentReviewDialog(results, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_comments = dialog.get_selected_comments()
                self.update_log(f"User selected {len(selected_comments)} comments for posting.")
                self.post_selected_comments(selected_comments)
            else:
                self.update_log("User cancelled comment review.")
        else:
            self.update_log("Automatically posting all generated comments...")
            self.post_selected_comments(results)
        self.display_results(results)

    def post_selected_comments(self, selected_comments):
        self.update_log(f"Preparing to post {len(selected_comments)} comments...")
        for comment in selected_comments:
            wait_time = random.uniform(self.min_wait_time.value(), self.max_wait_time.value())
            self.update_log(f"Waiting {wait_time:.2f} seconds before posting comment...")
            time.sleep(wait_time)
        
            self.update_log(f"Posting comment for '{comment['title']}' in r/{comment['subreddit']}...")
            self.update_log(f"Comment URL: {comment.get('url', 'URL not available')}")
            self.update_log(f"AI Comment: {comment['ai_comment'][:100]}...")  # Log first 100 chars of the comment
        
            try:
                if 'url' not in comment or not comment['url']:
                    raise ValueError("Comment URL is missing or empty")
            
                success = post_comment(self.driver, comment['ai_comment'], comment['url'])
            
                if success:
                    self.update_log(f"Successfully posted comment in r/{comment['subreddit']}")
                else:
                    self.update_log(f"Failed to post comment in r/{comment['subreddit']}")
            except Exception as e:
                self.update_log(f"Error posting comment: {str(e)}")
                self.update_log(f"Full error details: {traceback.format_exc()}")

        self.update_status("Finished posting selected comments")
        self.update_log("All selected comments have been processed.")
        self.start_button.setEnabled(True)
            
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
        dialog = ProxySettingsDialog(self)
        dialog.set_proxy_settings(self.proxy_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.proxy_settings = dialog.get_proxy_settings()
            self.update_status("Proxy settings updated")

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