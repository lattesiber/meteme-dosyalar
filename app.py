import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QScrollArea, QFrame, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QDrag
from PyQt6.QtMultimedia import QSoundEffect

# -----------------------------
# Blok Sınıfı
# -----------------------------
class DraggableBlock(QFrame):
    def __init__(self, text, color="#6a0dad", editable=False, workspace=None):
        super().__init__()
        self.workspace = workspace
        self.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.editable = editable
        self.text = text
        if editable:
            self.text_field = QLineEdit(text)
            self.text_field.setStyleSheet(
                "background-color: rgba(255,255,255,0.2); color: white; font-weight: bold; border: none; padding-left: 5px;"
            )
            self.layout.addWidget(self.text_field)
        else:
            self.label = QLabel(text)
            self.label.setStyleSheet("color: white; font-weight: bold; padding-left: 10px;")
            self.layout.addWidget(self.label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.workspace:
            # Sağ tıklama ile blok kaldır
            self.workspace.layout.removeWidget(self)
            self.deleteLater()
            return
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.get_text())
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)

    def get_text(self):
        if self.editable:
            return self.text_field.text()
        else:
            return self.text

# -----------------------------
# Çalışma Alanı
# -----------------------------
class Workspace(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2a2a2a; border: 2px dashed #555; border-radius: 10px;")
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10,10,10,10)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        text = event.mimeData().text()
        color_map = {
            "Merhaba Yaz": "#ff4b4b",
            "Özel Yazı": "#ff944b",
            "Sayıyı 1 Arttır": "#4bafff",
            "Bekle 1s": "#4bff88",
            "Döngü Başlat": "#ffb84b",
            "Koşul": "#b84bff",
            "Renk Değiştir": "#4bffdf",
            "Ses Çal": "#ff4bd6",
            "Dur": "#ff4b4b",
            "Sonsuz Döngü": "#4b88ff"
        }
        editable = text == "Özel Yazı"
        block = DraggableBlock(text, color_map.get(text, "#6a0dad"), editable=editable, workspace=self)
        self.layout.addWidget(block)

# -----------------------------
# Ana Uygulama
# -----------------------------
class MetemeFull(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meteme")
        self.setGeometry(50, 50, 1300, 750)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # -----------------------------
        # Ana panel: Sol blok + Çalışma alanı
        # -----------------------------
        content_layout = QHBoxLayout()
        self.main_layout.addLayout(content_layout)

        # Sol Panel: Temel bloklar scrollable
        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5,5,5,5)
        left_layout.setSpacing(5)
        left_container.setLayout(left_layout)

        scroll_left = QScrollArea()
        scroll_left.setWidgetResizable(True)
        scroll_left.setWidget(left_container)
        content_layout.addWidget(scroll_left, 2)

        # Temel bloklar
        blocks = [
            "Merhaba Yaz", "Özel Yazı", "Sayıyı 1 Arttır", "Bekle 1s",
            "Döngü Başlat", "Koşul", "Renk Değiştir", "Ses Çal",
            "Dur", "Sonsuz Döngü"
        ]
        colors = ["#ff4b4b","#ff944b","#4bafff","#4bff88","#ffb84b","#b84bff","#4bffdf","#ff4bd6","#ffc34b","#4b88ff"]

        for i, name in enumerate(blocks):
            editable = name == "Özel Yazı"
            block = DraggableBlock(name, colors[i % len(colors)], editable=editable)
            left_layout.addWidget(block)
        left_layout.addStretch()

        # Çalışma Alanı
        workspace_container = QWidget()
        workspace_layout = QVBoxLayout()
        workspace_layout.setContentsMargins(5,5,5,5)
        workspace_layout.setSpacing(5)
        workspace_container.setLayout(workspace_layout)

        self.workspace = Workspace()
        scroll_workspace = QScrollArea()
        scroll_workspace.setWidgetResizable(True)
        scroll_workspace.setWidget(self.workspace)
        scroll_workspace.setStyleSheet("border: 2px solid #444;")
        workspace_layout.addWidget(scroll_workspace)

        # Çalıştır butonu
        self.run_button = QPushButton("Çalıştır")
        self.run_button.setStyleSheet("""
            background-color: #ff4b4b;
            color: white;
            padding: 15px;
            font-size: 16px;
            border-radius: 10px;
        """)
        self.run_button.clicked.connect(self.run_blocks)
        workspace_layout.addWidget(self.run_button)

        # Çıktı alanı
        self.output = QLabel("Çıktı burada görünecek")
        self.output.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444; padding: 10px;")
        self.output.setFixedHeight(200)
        workspace_layout.addWidget(self.output)

        content_layout.addWidget(workspace_container, 5)

        # -----------------------------
        # Ses Efekti
        # -----------------------------
        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile("pop.wav"))
        self.sound_effect.setVolume(0.7)

    # -----------------------------
    # Blokları Çalıştırma Fonksiyonu
    # -----------------------------
    def run_blocks(self):
        result = ""
        for i in range(self.workspace.layout.count()):
            widget = self.workspace.layout.itemAt(i).widget()
            if widget:
                text = widget.get_text()
                if text == "Merhaba Yaz":
                    result += "Merhaba!\n"
                elif text == "Özel Yazı":
                    result += f"{text}\n"
                elif text == "Sayıyı 1 Arttır":
                    result += "Sayı: 1\n"
                elif text == "Bekle 1s":
                    result += "1 saniye bekledik...\n"
                elif text == "Döngü Başlat":
                    result += "Döngü başlatıldı...\n"
                elif text == "Koşul":
                    result += "Koşul kontrol edildi...\n"
                elif text == "Renk Değiştir":
                    result += "Renk değiştirildi...\n"
                elif text == "Ses Çal":
                    result += "Ses çalındı...\n"
                    self.sound_effect.play()
                elif text == "Dur":
                    result += "Duruldu.\n"
                elif text == "Sonsuz Döngü":
                    result += "Sonsuz döngü simülasyonu...\n"
        self.output.setText(result)

# -----------------------------
# Program Başlat
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MetemeFull()
    window.show()
    sys.exit(app.exec())
