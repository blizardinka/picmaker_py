import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton
from PySide6.QtGui import QPixmap
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Diagonal Border Image Creator")
        self.setGeometry(100, 100, 800, 450)

        self.layout = QVBoxLayout()

        self.angle_label = QLabel("Angle:")
        self.layout.addWidget(self.angle_label)
        self.angle_entry = QLineEdit("30")
        self.layout.addWidget(self.angle_entry)

        self.thickness_label = QLabel("Frame Thickness:")
        self.layout.addWidget(self.thickness_label)
        self.thickness_entry = QLineEdit("20")
        self.layout.addWidget(self.thickness_entry)

        self.border_label = QLabel("Border Size:")
        self.layout.addWidget(self.border_label)
        self.border_entry = QLineEdit("40")
        self.layout.addWidget(self.border_entry)

        self.update_button = QPushButton("Update Image")
        self.update_button.clicked.connect(self.update_image)
        self.layout.addWidget(self.update_button)

        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def create_image_with_diagonal_border(self, width, height, frame_thickness, border_size, colors, angle):
        scale_factor = 8
        high_res_width = width * scale_factor
        high_res_height = height * scale_factor
        high_res_frame_thickness = frame_thickness * scale_factor
        high_res_border_size = border_size * scale_factor

        angle_radians = math.radians(angle)
        image = Image.new("RGB", (high_res_width, high_res_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        tan_angle = math.tan(angle_radians)
        extended_range = max(high_res_width, high_res_height) * 4

        for idx, i in enumerate(range(-extended_range, extended_range, high_res_frame_thickness)):
            color = colors[idx % len(colors)]
            start_x = i
            start_y = -extended_range
            end_x = i + extended_range / tan_angle
            end_y = extended_range
            draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=high_res_frame_thickness)

        draw.rectangle([high_res_border_size, high_res_border_size, high_res_width - high_res_border_size, high_res_height - high_res_border_size], fill=(255, 255, 255))
        image = image.resize((width, height), Image.LANCZOS)
        return image

    def update_image(self):
        angle = int(self.angle_entry.text())
        frame_thickness = int(self.thickness_entry.text())
        border_size = int(self.border_entry.text())
        colors = [(0, 0, 0), (51, 129, 138), (160, 236, 246), (249, 147, 78), (236, 249, 247)]
        image = self.create_image_with_diagonal_border(800, 400, frame_thickness, border_size, colors, angle)
        qimage = ImageQt(image)
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)
        
        # Save the image to a file
        output_path = "output_image.png"
        image.save(output_path)
        print(f"Image saved to {output_path}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
