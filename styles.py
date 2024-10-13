def apply_dark_theme(app):
    app.setStyleSheet("""
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

def style_save_button(button):
    button.setStyleSheet("""
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

def style_advanced_settings_button(button):
    button.setStyleSheet("""
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

def style_start_button(button):
    button.setStyleSheet("""
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
