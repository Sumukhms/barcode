import sys
import cv2
from pyzbar.pyzbar import decode
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

class BarcodeScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Barcode and QR Code Scanner")
        self.setGeometry(100, 100, 800, 600)

        # Initialize camera variables
        self.cap = None
        self.running = False

        # UI Components
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(640, 480)
        self.camera_label.setStyleSheet("background-color: black;")

        self.data_text = QTextEdit(self)
        self.data_text.setReadOnly(True)
        self.data_text.setPlaceholderText("Decoded data will appear here...")

        self.start_button = QPushButton("Start Camera", self)
        self.start_button.clicked.connect(self.start_camera)

        self.stop_button = QPushButton("Stop Camera", self)
        self.stop_button.clicked.connect(self.stop_camera)

        self.upload_button = QPushButton("Upload Photo", self)
        self.upload_button.clicked.connect(self.upload_photo)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.camera_label)
        layout.addWidget(self.data_text)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.upload_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for updating frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)

    def start_camera(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set higher resolution
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            if not self.cap.isOpened():
                self.data_text.append("Error: Unable to access webcam.")
                return

            self.running = True
            self.timer.start(10)
            self.data_text.append("Camera started.")

    def stop_camera(self):
        self.running = False
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.camera_label.clear()
        self.data_text.append("Camera stopped.")

    def update_camera(self):
        if self.running and self.cap:
            success, img = self.cap.read()
            if success:
                # Decode barcodes and QR codes
                detected_data = self.decode_barcodes(img)

                if detected_data:
                    for data in detected_data:
                        self.data_text.append(f"Detected: {data}")
                        self.data_text.verticalScrollBar().setValue(
                            self.data_text.verticalScrollBar().maximum()
                        )

                # Convert image to QPixmap for display
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, ch = img.shape
                bytes_per_line = ch * w
                q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.camera_label.setPixmap(pixmap)

    def decode_barcodes(self, img):
        """
        Decode barcodes and QR codes from the image.
        Return the decoded data.
        """
        detected_data = []
        # Use pyzbar to decode QR and barcodes
        for barcode in decode(img):
            myData = barcode.data.decode('utf-8')
            detected_data.append(myData)

            # Draw bounding box and label
            pts = barcode.polygon
            if len(pts) == 4:
                pts = [tuple(point) for point in pts]
                cv2.polylines(img, [np.array(pts, dtype=np.int32)], True, (0, 255, 0), 2)
                cv2.putText(img, myData, (pts[0][0], pts[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return detected_data

    def upload_photo(self):
        # Open file dialog to choose an image
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            # Read the uploaded image
            img = cv2.imread(file_name)
            if img is None:
                self.data_text.append("Error: Unable to read the image file.")
                return
            
            # Decode barcodes and QR codes from the uploaded image
            detected_data = self.decode_barcodes(img)

            if detected_data:
                for data in detected_data:
                    self.data_text.append(f"Detected: {data}")
            else:
                self.data_text.append("No barcode or QR code detected.")

            # Convert image to QPixmap for display
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img.shape
            bytes_per_line = ch * w
            q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.camera_label.setPixmap(pixmap)


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarcodeScannerApp()
    window.show()
    sys.exit(app.exec_())
