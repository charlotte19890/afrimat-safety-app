import sys
import threading
import speech_recognition as sr
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTextEdit, QMessageBox, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt


class AfrimatSafetyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Afrimat Safety & Compliance Demo")
        self.setGeometry(200, 200, 650, 500)

        self.init_ui()
        self.recognizer = sr.Recognizer()
        self.is_listening = False

    def init_ui(self):
        main_layout = QVBoxLayout()

        header = QLabel("AFRIMAT SAFETY & COMPLIANCE")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            "background-color: #B00000; color: white; padding: 12px; "
            "font-size: 22px; font-weight: bold;"
        )
        main_layout.addWidget(header)

        info = QLabel(
            "• Capture daily safety notes\n"
            "• Report incidents using voice input\n"
            "• Save or clear reports easily"
        )
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 14px; margin: 10px;")
        main_layout.addWidget(info)

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Safety notes and incident reports will appear here...")
        self.text_area.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.text_area)

        button_row = QHBoxLayout()

        self.checklist_button = QPushButton("Daily Checklist")
        self.checklist_button.clicked.connect(self.fill_checklist)
        self.checklist_button.setStyleSheet(self.button_style())
        button_row.addWidget(self.checklist_button)

        self.voice_button = QPushButton("Record Voice")
        self.voice_button.clicked.connect(self.toggle_voice_recording)
        self.voice_button.setStyleSheet(self.button_style())
        button_row.addWidget(self.voice_button)

        self.save_button = QPushButton("Save Report")
        self.save_button.clicked.connect(self.save_report)
        self.save_button.setStyleSheet(self.button_style())
        button_row.addWidget(self.save_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_report)
        self.clear_button.setStyleSheet(self.button_style())
        button_row.addWidget(self.clear_button)

        main_layout.addLayout(button_row)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "background-color: #F0F0F0; padding: 6px; font-size: 13px;"
        )
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def button_style(self):
        return (
            "background-color: #B00000; color: white; padding: 10px; "
            "font-size: 14px; border-radius: 5px;"
        )

    def fill_checklist(self):
        template = (
            "DAILY SAFETY CHECKLIST\n"
            "----------------------\n"
            "PPE Checked: Yes / No\n"
            "Equipment Condition: Good / Needs Attention\n"
            "Hazards Observed: ______________________\n"
            "Supervisor: ______________________\n"
            "Signature: ______________________\n"
        )
        self.text_area.setPlainText(template)
        self.status_label.setText("Status: Checklist loaded")

    def toggle_voice_recording(self):
        if not self.is_listening:
            self.is_listening = True
            self.voice_button.setText("Stop")
            self.status_label.setText("Status: Listening... Speak now")
            threading.Thread(target=self.record_voice, daemon=True).start()
        else:
            self.is_listening = False
            self.voice_button.setText("Record Voice")
            self.status_label.setText("Status: Stopping...")

    def record_voice(self):
        with sr.Microphone() as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, phrase_time_limit=10)

                self.status_label.setText("Status: Processing voice...")
                text = self.recognizer.recognize_google(audio)

                current = self.text_area.toPlainText()
                if current:
                    current += "\n\n"
                current += "INCIDENT REPORT (Voice):\n" + text
                self.text_area.setPlainText(current)

                self.status_label.setText("Status: Voice captured")
            except sr.UnknownValueError:
                self.show_error("I couldn't understand the audio.")
                self.status_label.setText("Status: Ready")
            except sr.RequestError as e:
                self.show_error(f"Speech service error: {e}")
                self.status_label.setText("Status: Ready")
            finally:
                self.is_listening = False
                self.voice_button.setText("Record Voice")

    def save_report(self):
        text = self.text_area.toPlainText()
        if not text.strip():
            self.show_error("There is no report to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "", "Text Files (*.txt)"
        )
        if file_path:
            with open(file_path, "w") as file:
                file.write(text)
            self.status_label.setText("Status: Report saved")

    def clear_report(self):
        self.text_area.clear()
        self.status_label.setText("Status: Cleared")

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AfrimatSafetyApp()
    window.show()
    sys.exit(app.exec_())


