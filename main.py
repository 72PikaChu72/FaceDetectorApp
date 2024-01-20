import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QComboBox, QPushButton, QFileDialog,QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QTimer,Qt
from time import sleep
import cv2

class FaceDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.mirror = False  # Переменная для хранения информации о том, отзеркалено ли изображение
        icon = QIcon('icon.png')  # Замените 'path_to_icon.png' на путь к вашей иконке
        self.video_sources = None
        
        # Фиксированный размер окна
        self.setFixedSize(1000, 800)
        
        # Установка иконки для окна
        self.setWindowIcon(icon)
        
        self.video_sources = self.list_ports()
        
        # Установка главного слоя для основного виджета
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Устранение ошибки при отсутствии камеры
        self.CameraNotFoundLabel = QLabel("Камера не найдена")
        self.CameraNotFoundLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.CameraNotFoundLabel)
        
        while len(self.video_sources) == 0:
            self.video_sources = self.list_ports()
            return
        self.layout.removeWidget(self.CameraNotFoundLabel)
        self.selected_video_source = 0

        self.video_source = 0  # Индекс веб-камеры (может потребоваться изменение в зависимости от вашей конфигурации)
        self.vid = cv2.VideoCapture(self.video_source)

        self.label = QLabel()
        
        
        
        self.video_source_combobox = QComboBox()
        self.video_source_combobox.addItems(map(str, self.video_sources))
        self.video_source_combobox.currentIndexChanged.connect(self.update_video_source)
        
        self.text = QLabel("Изменить источник видео")
        self.snapshot_button = QPushButton("Сделать снимок")
        self.snapshot_button.clicked.connect(self.take_snapshot)

        self.mirror_button = QPushButton("Зеркальное изображение")
        self.mirror_button.clicked.connect(self.mirror_image)
        # Создание горизонтального слоя для текста и комбобокса
        self.box = QHBoxLayout()
        self.box.setSpacing(0)
        self.box.addWidget(self.text)
        self.box.addWidget(self.video_source_combobox)

        # Добавление виджетов и слоев в основной слой
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.box)
        self.layout.addWidget(self.snapshot_button)
        self.layout.addWidget(self.mirror_button)

        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(0)
        
        
        

    def update_frame(self):
        ret, frame = self.vid.read()

        if ret:
            processed_frame = self.detect_faces(frame)

            if self.mirror:
                processed_frame = cv2.flip(processed_frame, 1)  # Отзеркалить изображение

            height, width, channel = processed_frame.shape

            # Изменение размера изображения так, чтобы оно вписывалось в окно, сохраняя пропорции
            aspect_ratio = width / height
            new_width = min(self.width(), int(self.height() * aspect_ratio))
            new_height = min(self.height(), int(new_width / aspect_ratio))

            processed_frame = cv2.resize(processed_frame, (new_width, new_height))

            bytes_per_line = 3 * new_width
            q_image = QImage(processed_frame.data, new_width, new_height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image = pixmap
            self.label.setPixmap(pixmap)

    def detect_faces(self, frame):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def closeEvent(self, event):
        self.vid.release()

    def list_ports(self):
        is_working = True
        dev_port = 0
        working_ports = []
        available_ports = []
        while is_working:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                is_working = False
            else:
                is_reading, _ = camera.read()
                if is_reading:
                    working_ports.append(dev_port)
                else:
                    available_ports.append(dev_port)
            dev_port += 1
        return working_ports

    def update_video_source(self):
        self.selected_video_source = int(self.video_source_combobox.currentText())
        self.vid.release()
        self.vid = cv2.VideoCapture(self.selected_video_source)

    def take_snapshot(self):
        saved_image = self.image
        if saved_image:
            # Открытие диалогового окна для выбора файла сохранения
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить снимок", "", "PNG files (*.png);;All files (*)")

            if file_path:
                # Сохранение изображения
                saved_image.save(file_path)

    def mirror_image(self):
        self.mirror = not self.mirror  # Инвертировать значение зеркальности

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceDetectorApp()
    window.setWindowTitle("Face Detector App")
    window.show()
    sys.exit(app.exec_())