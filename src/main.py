import os
from PIL import Image
from huffman import (
    huffman_encode,
    huffman_decode,
    build_codes,
    calculate_efficiency,
    HuffmanNode,
    build_huffman_tree,
    tuple_huffman_decode,
)
from utils import split_image_channels, merge_image_channels, save_image
from visualization import save_huffman_tree_graph, print_huffman_tree_graphviz
from tkinter import Tk, filedialog
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QFileDialog,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QStackedWidget,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGridLayout,
)
from PyQt5.QtGui import QPixmap, QImage, QWheelEvent, QPainter, QPen
from PyQt5.QtCore import QTimer, Qt, QRectF
import sys
import heapq
import graphviz
from collections import Counter


class HuffmanNode:
    def __init__(self, symbol=None, weight=0, word=None, left=None, right=None):
        self.symbol = symbol
        self.weight = weight
        self.word = word
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.weight < other.weight


class ImageWindow(QWidget):
    def __init__(self, title, pixmap, info, stacked_widget):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowState(Qt.WindowMaximized)

        layout = QVBoxLayout()
        self.setLayout(layout)

        info_label = QLabel(info)
        info_label.setStyleSheet("font-size: 16px; color: black;")
        layout.addWidget(info_label)

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        self.add_image(pixmap)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #f0f0f0;"
        )
        if stacked_widget is not None:
            back_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        button_layout.addWidget(back_button)

        # Set background color to white
        self.setStyleSheet("background-color: white;")

        # Enable zooming
        self.view.wheelEvent = self.wheelEvent

        # Set initial zoom level
        self.current_zoom = 1.0

    def add_image(self, pixmap):
        # Create a QGraphicsPixmapItem for the image
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Position the image
        pixmap_item.setPos(10, 10)

        # Scale the image to fit the view
        self.scale_image_to_fit_view(pixmap_item)

        # Center the image
        self.view.setAlignment(Qt.AlignCenter)

    def scale_image_to_fit_view(self, pixmap_item):
        view_rect = self.view.viewport().rect()
        scene_rect = self.view.mapToScene(view_rect).boundingRect()
        pixmap_rect = pixmap_item.boundingRect()

        scale_factor = min(
            scene_rect.width() / pixmap_rect.width(),
            scene_rect.height() / pixmap_rect.height(),
        )
        pixmap_item.setScale(scale_factor)
        self.current_zoom = scale_factor

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor

            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor

            self.view.scale(zoom_factor, zoom_factor)
            self.current_zoom *= zoom_factor
        else:
            # Pan the view
            delta = event.angleDelta()
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() - delta.x()
            )
            self.view.verticalScrollBar().setValue(
                self.view.verticalScrollBar().value() - delta.y()
            )


class GraphWindow(QWidget):
    def __init__(
        self, title, pixmap, stacked_widget, frequencies, show_step_by_step_graph
    ):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowState(Qt.WindowMaximized)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        self.add_image(pixmap)

        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 16px; color: black;")
        layout.addWidget(self.info_label)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #f0f0f0;"
        )
        back_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        button_layout.addWidget(back_button)

        step_button = QPushButton("Step by Step Graph")
        step_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #f0f0f0;"
        )
        step_button.clicked.connect(lambda: show_step_by_step_graph(title, frequencies))
        button_layout.addWidget(step_button)

        # Set background color to white
        self.setStyleSheet("background-color: white;")

        # Enable zooming
        self.view.wheelEvent = self.wheelEvent

        # Set initial zoom level
        self.current_zoom = 1.0

    def add_image(self, pixmap):
        # Create a QGraphicsPixmapItem for the image
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Position the image
        pixmap_item.setPos(10, 10)

        # Scale the image to fit the view
        self.scale_image_to_fit_view(pixmap_item)

        # Center the image
        self.view.setAlignment(Qt.AlignCenter)

    def scale_image_to_fit_view(self, pixmap_item):
        view_rect = self.view.viewport().rect()
        scene_rect = self.view.mapToScene(view_rect).boundingRect()
        pixmap_rect = pixmap_item.boundingRect()

        scale_factor = min(
            scene_rect.width() / pixmap_rect.width(),
            scene_rect.height() / pixmap_rect.height(),
        )
        pixmap_item.setScale(scale_factor)
        self.current_zoom = scale_factor

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor

            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor

            self.view.scale(zoom_factor, zoom_factor)
            self.current_zoom *= zoom_factor
        else:
            # Pan the view
            delta = event.angleDelta()
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() - delta.x()
            )
            self.view.verticalScrollBar().setValue(
                self.view.verticalScrollBar().value() - delta.y()
            )

    def set_info(self, info):
        self.info_label.setText(info)


class StepByStepGraphWindow(QWidget):
    def __init__(self, title, stacked_widget, steps, output_dir):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowState(Qt.WindowMaximized)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        back_button = QPushButton("Back to Main Menu")
        back_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #f0f0f0;"
        )
        back_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        button_layout.addWidget(back_button)

        prev_button = QPushButton("Previous Step")
        prev_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #f0f0f0;"
        )
        prev_button.clicked.connect(self.prev_step)
        button_layout.addWidget(prev_button)

        next_button = QPushButton("Next Step")
        next_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #f0f0f0;"
        )
        next_button.clicked.connect(self.next_step)
        button_layout.addWidget(next_button)

        # Set background color to white
        self.setStyleSheet("background-color: white;")

        # Initialize step-by-step building variables
        self.steps = steps
        self.current_step = 0
        self.output_dir = output_dir

        # Enable zooming
        self.current_zoom = 1.0

        # Load the first step image
        self.load_step_image()

    def load_step_image(self):
        step_image_path = os.path.join(self.output_dir, f"step_{self.current_step}.png")
        pixmap = QPixmap(step_image_path)
        self.scene.clear()
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.view.setSceneRect(QRectF(pixmap.rect()))
        self.view.resetTransform()
        self.view.scale(self.current_zoom, self.current_zoom)

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.load_step_image()

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.load_step_image()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor

            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor

            self.current_zoom *= zoom_factor
            self.view.scale(zoom_factor, zoom_factor)
        else:
            # Pan the view
            delta = event.angleDelta()
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() - delta.x()
            )
            self.view.verticalScrollBar().setValue(
                self.view.verticalScrollBar().value() - delta.y()
            )


def main():
    # Clear the terminal
    os.system("cls" if os.name == "nt" else "clear")

    # Open file dialog to select an image
    Tk().withdraw()  # We don't want a full GUI, so keep the root window from appearing
    initial_dir = os.path.join(os.getcwd(), "huffman_rgb_project", "ImágenesPrueba")
    image_path = filedialog.askopenfilename(
        initialdir=initial_dir,
        title="Select an image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")),
    )
    if not image_path:
        print("No image selected.")
        return

    print("Loading image...")
    image = Image.open(image_path).convert("RGB")

    # Split the image into RGB channels
    print("Splitting image into RGB channels...")
    r_channel, g_channel, b_channel = split_image_channels(image)

    # Encode each channel using Huffman coding
    print("Encoding RGB channels...")
    encoded_r, huffman_tree_r, frequencies_r, steps_r, encoded_data_r = huffman_encode(
        list(r_channel.getdata())
    )
    encoded_g, huffman_tree_g, frequencies_g, steps_g, encoded_data_g = huffman_encode(
        list(g_channel.getdata())
    )
    encoded_b, huffman_tree_b, frequencies_b, steps_b, encoded_data_b = huffman_encode(
        list(b_channel.getdata())
    )

    # Create a subfolder in huffman_rgb_project/results with the date and the name of the image
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    subfolder_name = f"{timestamp}_{os.path.splitext(os.path.basename(image_path))[0]}"
    subfolder_path = os.path.join("huffman_rgb_project", "results", subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    # Create subfolders for the splitted images, Huffman tree graphs, and encoded text files
    splitted_images_path = os.path.join(subfolder_path, "splitted_images")
    os.makedirs(splitted_images_path, exist_ok=True)
    rgb_graphs_path = os.path.join(subfolder_path, "rgb_graphs")
    os.makedirs(rgb_graphs_path, exist_ok=True)
    rgb_codes_path = os.path.join(subfolder_path, "rgb_codes")
    os.makedirs(rgb_codes_path, exist_ok=True)

    # Save the Huffman tree graphs for each channel
    print("Saving Huffman tree graphs...")
    code_map_r = build_codes(huffman_tree_r)
    code_map_g = build_codes(huffman_tree_g)
    code_map_b = build_codes(huffman_tree_b)
    save_huffman_tree_graph(
        huffman_tree_r,
        frequencies_r,
        os.path.join(rgb_graphs_path, "Red_Channel_Huffman_Tree"),
        code_map_r,
    )
    save_huffman_tree_graph(
        huffman_tree_g,
        frequencies_g,
        os.path.join(rgb_graphs_path, "Green_Channel_Huffman_Tree"),
        code_map_g,
    )
    save_huffman_tree_graph(
        huffman_tree_b,
        frequencies_b,
        os.path.join(rgb_graphs_path, "Blue_Channel_Huffman_Tree"),
        code_map_b,
    )

    # Save each channel image
    print("Saving each channel image...")
    r_image = Image.merge(
        "RGB",
        (r_channel, Image.new("L", r_channel.size), Image.new("L", r_channel.size)),
    )
    g_image = Image.merge(
        "RGB",
        (Image.new("L", g_channel.size), g_channel, Image.new("L", g_channel.size)),
    )
    b_image = Image.merge(
        "RGB",
        (Image.new("L", b_channel.size), Image.new("L", b_channel.size), b_channel),
    )
    r_image.save(os.path.join(splitted_images_path, "Red_Channel.jpg"))
    g_image.save(os.path.join(splitted_images_path, "Green_Channel.jpg"))
    b_image.save(os.path.join(splitted_images_path, "Blue_Channel.jpg"))

    # Generate encoded words and save the encoded image text for each channel as a .txt file
    print("Generating encoded words...")
    pixels_r = list(r_channel.getdata())
    encoded_words_r = [code_map_r[pixel] for pixel in pixels_r]
    separated_code_r = "-".join(encoded_words_r)
    print("Separated code for Red channel by dash...")

    pixels_g = list(g_channel.getdata())
    encoded_words_g = [code_map_g[pixel] for pixel in pixels_g]
    separated_code_g = "-".join(encoded_words_g)
    print("Separated code for Green channel by dash...")

    pixels_b = list(b_channel.getdata())
    encoded_words_b = [code_map_b[pixel] for pixel in pixels_b]
    separated_code_b = "-".join(encoded_words_b)
    print("Separated code for Blue channel by dash...")

    print("Creating text file for encoded text...")
    encoded_text_file_name_r = os.path.join(
        rgb_codes_path,
        f"Codigo_Red_{os.path.splitext(os.path.basename(image_path))[0]}.txt",
    )
    with open(encoded_text_file_name_r, "w") as f:
        f.write(separated_code_r)
    encoded_text_file_name_g = os.path.join(
        rgb_codes_path,
        f"Codigo_Green_{os.path.splitext(os.path.basename(image_path))[0]}.txt",
    )
    with open(encoded_text_file_name_g, "w") as f:
        f.write(separated_code_g)
    encoded_text_file_name_b = os.path.join(
        rgb_codes_path,
        f"Codigo_Blue_{os.path.splitext(os.path.basename(image_path))[0]}.txt",
    )
    with open(encoded_text_file_name_b, "w") as f:
        f.write(separated_code_b)

    # Calculate and print Huffman's coding efficiency for each channel
    entropy_r, avg_length_r, efficiency_r = calculate_efficiency(
        frequencies_r, code_map_r
    )
    entropy_g, avg_length_g, efficiency_g = calculate_efficiency(
        frequencies_g, code_map_g
    )
    entropy_b, avg_length_b, efficiency_b = calculate_efficiency(
        frequencies_b, code_map_b
    )
    print(
        f"Red channel - Entropy: {entropy_r:.4f}, Average length: {avg_length_r:.4f}, Efficiency: {efficiency_r:.4f}"
    )
    print(
        f"Green channel - Entropy: {entropy_g:.4f}, Average length: {avg_length_g:.4f}, Efficiency: {efficiency_g:.4f}"
    )
    print(
        f"Blue channel - Entropy: {entropy_b:.4f}, Average length: {avg_length_b:.4f}, Efficiency: {efficiency_b:.4f}"
    )

    # Find and print the longest encoded word for each channel
    max_word_length_r = max(len(word) for word in encoded_words_r)
    max_word_length_g = max(len(word) for word in encoded_words_g)
    max_word_length_b = max(len(word) for word in encoded_words_b)
    longest_word_r = max(encoded_words_r, key=len)
    longest_word_g = max(encoded_words_g, key=len)
    longest_word_b = max(encoded_words_b, key=len)
    print(f"Red channel - Longest encoded word length: {max_word_length_r}")
    print(f"Green channel - Longest encoded word length: {max_word_length_g}")
    print(f"Blue channel - Longest encoded word length: {max_word_length_b}")

    # Save the average length, entropy, efficiency, and longest word length to a file for each channel
    huffman_coding_info_r = (
        f"Red channel:\n"
        f"Average length of the encoded symbols: {avg_length_r:.4f}\n"
        f"Entropy of the source: {entropy_r:.4f}\n"
        f"Huffman's coding efficiency: {efficiency_r:.4f}\n"
        f"Longest encoded word: {longest_word_r} (length: {max_word_length_r})\n"
    )
    huffman_coding_file_path_r = os.path.join(
        rgb_graphs_path, "Huffmans_Coding_Red.txt"
    )
    with open(huffman_coding_file_path_r, "w") as f:
        f.write(huffman_coding_info_r)

    huffman_coding_info_g = (
        f"Green channel:\n"
        f"Average length of the encoded symbols: {avg_length_g:.4f}\n"
        f"Entropy of the source: {entropy_g:.4f}\n"
        f"Huffman's coding efficiency: {efficiency_g:.4f}\n"
        f"Longest encoded word: {longest_word_g} (length: {max_word_length_g})\n"
    )
    huffman_coding_file_path_g = os.path.join(
        rgb_graphs_path, "Huffmans_Coding_Green.txt"
    )
    with open(huffman_coding_file_path_g, "w") as f:
        f.write(huffman_coding_info_g)

    huffman_coding_info_b = (
        f"Blue channel:\n"
        f"Average length of the encoded symbols: {avg_length_b:.4f}\n"
        f"Entropy of the source: {entropy_b:.4f}\n"
        f"Huffman's coding efficiency: {efficiency_b:.4f}\n"
        f"Longest encoded word: {longest_word_b} (length: {max_word_length_b})\n"
    )
    huffman_coding_file_path_b = os.path.join(
        rgb_graphs_path, "Huffmans_Coding_Blue.txt"
    )
    with open(huffman_coding_file_path_b, "w") as f:
        f.write(huffman_coding_info_b)

    # Decode each channel
    print("Decoding RGB channels...")
    decoded_r = huffman_decode(encoded_data_r, huffman_tree_r, r_channel.size)
    decoded_g = huffman_decode(encoded_data_g, huffman_tree_g, g_channel.size)
    decoded_b = huffman_decode(encoded_data_b, huffman_tree_b, b_channel.size)

    # Merge the decoded channels back into a single image
    print("Merging decoded channels back into a single image...")
    restored_image = merge_image_channels(decoded_r, decoded_g, decoded_b)

    # Save the restored image
    output_path = os.path.join(subfolder_path, "restored_image.jpg")
    save_image(restored_image, output_path)
    print(f"Restored image saved as {output_path}")

    # Save a copy of the original image in the subfolder
    image.save(os.path.join(subfolder_path, "Original.jpg"))

    print("Process completed successfully.")

    # Create the GUI to display the images and information
    create_gui(subfolder_path, image_path, frequencies_r, frequencies_g, frequencies_b)


def create_gui(
    subfolder_path, original_image_path, frequencies_r, frequencies_g, frequencies_b
):
    app = QApplication(sys.argv)

    # Load images
    original_image = Image.open(original_image_path)
    red_image = Image.open(
        os.path.join(subfolder_path, "splitted_images", "Red_Channel.jpg")
    )
    green_image = Image.open(
        os.path.join(subfolder_path, "splitted_images", "Green_Channel.jpg")
    )
    blue_image = Image.open(
        os.path.join(subfolder_path, "splitted_images", "Blue_Channel.jpg")
    )
    restored_image = Image.open(os.path.join(subfolder_path, "restored_image.jpg"))

    # Load Huffman tree graphs
    red_graph = Image.open(
        os.path.join(subfolder_path, "rgb_graphs", "Red_Channel_Huffman_Tree.png")
    )
    green_graph = Image.open(
        os.path.join(subfolder_path, "rgb_graphs", "Green_Channel_Huffman_Tree.png")
    )
    blue_graph = Image.open(
        os.path.join(subfolder_path, "rgb_graphs", "Blue_Channel_Huffman_Tree.png")
    )

    # Convert images to QPixmap
    def pil2pixmap(image):
        image = image.convert("RGBA")
        data = image.tobytes("raw", "RGBA")
        qimage = QImage(data, image.size[0], image.size[1], QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimage)

    original_pixmap = pil2pixmap(original_image)
    red_pixmap = pil2pixmap(red_image)
    green_pixmap = pil2pixmap(green_image)
    blue_pixmap = pil2pixmap(blue_image)
    restored_pixmap = pil2pixmap(restored_image)
    red_graph_pixmap = pil2pixmap(red_graph)
    green_graph_pixmap = pil2pixmap(green_graph)
    blue_graph_pixmap = pil2pixmap(blue_graph)

    # Store window references to prevent garbage collection
    windows = []

    # Create the main menu
    main_menu = QWidget()
    main_menu_layout = QVBoxLayout()
    main_menu.setLayout(main_menu_layout)

    main_menu_label = QLabel("Huffman Coding Results")
    main_menu_label.setAlignment(Qt.AlignCenter)
    main_menu_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
    main_menu_layout.addWidget(main_menu_label)

    button_layout = QGridLayout()
    main_menu_layout.addLayout(button_layout)

    button_layout.addWidget(
        QPushButton(
            "Original Image",
            clicked=lambda: show_window(
                "Original Image", original_pixmap, "Original Image"
            ),
        ),
        0,
        0,
    )
    button_layout.addWidget(
        QPushButton(
            "Red Channel",
            clicked=lambda: show_window(
                "Red Channel",
                red_pixmap,
                read_file("Huffmans_Coding_Red.txt", subfolder_path),
            ),
        ),
        0,
        1,
    )
    button_layout.addWidget(
        QPushButton(
            "Green Channel",
            clicked=lambda: show_window(
                "Green Channel",
                green_pixmap,
                read_file("Huffmans_Coding_Green.txt", subfolder_path),
            ),
        ),
        1,
        0,
    )
    button_layout.addWidget(
        QPushButton(
            "Blue Channel",
            clicked=lambda: show_window(
                "Blue Channel",
                blue_pixmap,
                read_file("Huffmans_Coding_Blue.txt", subfolder_path),
            ),
        ),
        1,
        1,
    )
    button_layout.addWidget(
        QPushButton(
            "Restored Image",
            clicked=lambda: show_window(
                "Restored Image", restored_pixmap, "Restored Image"
            ),
        ),
        2,
        0,
    )
    button_layout.addWidget(
        QPushButton(
            "Red Channel Graph",
            clicked=lambda: show_graph(
                "Red Channel Huffman Tree", red_graph_pixmap, frequencies_r
            ),
        ),
        2,
        1,
    )
    button_layout.addWidget(
        QPushButton(
            "Green Channel Graph",
            clicked=lambda: show_graph(
                "Green Channel Huffman Tree", green_graph_pixmap, frequencies_g
            ),
        ),
        3,
        0,
    )
    button_layout.addWidget(
        QPushButton(
            "Blue Channel Graph",
            clicked=lambda: show_graph(
                "Blue Channel Huffman Tree", blue_graph_pixmap, frequencies_b
            ),
        ),
        3,
        1,
    )
    button_layout.addWidget(
        QPushButton(
            "Tuple Encoding",
            clicked=lambda: show_tuple_encoding(
                subfolder_path,
                original_image_path,
                stacked_widget,
                show_step_by_step_graph,
            ),
        ),
        4,
        0,
        1,
        2,
    )

    # Add some styling to the buttons
    for i in range(button_layout.count()):
        button = button_layout.itemAt(i).widget()
        button.setStyleSheet(
            "font-size: 20px; padding: 15px; background-color: #f0f0f0;"
        )

    # Set background color for the main menu
    main_menu.setStyleSheet("background-color: white;")

    # Create the stacked widget to manage different windows
    stacked_widget = QStackedWidget()
    stacked_widget.addWidget(main_menu)

    def show_window(title, pixmap, info):
        window = ImageWindow(title, pixmap, info, stacked_widget)
        windows.append(window)
        stacked_widget.addWidget(window)
        stacked_widget.setCurrentWidget(window)
        window.showMaximized()
        window.update()

    def show_graph(title, pixmap, frequencies):
        window = GraphWindow(
            title, pixmap, stacked_widget, frequencies, show_step_by_step_graph
        )
        windows.append(window)
        stacked_widget.addWidget(window)
        stacked_widget.setCurrentWidget(window)
        window.showMaximized()
        window.update()

    def show_step_by_step_graph(title, frequencies):
        output_dir = os.path.join(
            subfolder_path, "step_by_step_graphs", title.replace(" ", "_")
        )
        os.makedirs(output_dir, exist_ok=True)
        steps = generate_steps_for_graph(frequencies, output_dir)
        window = StepByStepGraphWindow(title, stacked_widget, steps, output_dir)
        windows.append(window)
        stacked_widget.addWidget(window)
        stacked_widget.setCurrentWidget(window)
        window.showMaximized()
        window.update()

    main_window = QWidget()
    main_window.setWindowTitle("Huffman Coding Results")
    main_window.setWindowState(Qt.WindowMaximized)

    layout = QVBoxLayout()
    main_window.setLayout(layout)
    layout.addWidget(stacked_widget)

    # Set background color for the main window
    main_window.setStyleSheet("background-color: white;")

    main_window.show()
    sys.exit(app.exec_())


def generate_steps_for_graph(frequencies, output_dir):
    steps = []
    nodes = [
        HuffmanNode(symbol, weight, word=symbol)
        for symbol, weight in frequencies.items()
    ]
    heapq.heapify(nodes)

    total_weight = sum(frequencies.values())

    # Initial step: show all words with their frequencies
    initial_dot = graphviz.Digraph()
    added_edges = set()
    for node in sorted(nodes, key=lambda x: x.weight):
        add_node_to_graph(
            initial_dot, node, added_edges=added_edges, total_weight=total_weight
        )
    try:
        initial_dot.render(filename=os.path.join(output_dir, "step_0"), format="png")
    except graphviz.backend.ExecutableNotFound:
        print("Warning: Graphviz executable not found. Skipping initial step.")
    except Exception as e:
        print(f"Warning: An error occurred while rendering the initial graph: {e}")
    steps.append(("initial", nodes.copy()))

    step_count = 1

    while len(nodes) > 1:
        lo = heapq.heappop(nodes)
        hi = heapq.heappop(nodes)
        new_node = HuffmanNode(weight=lo.weight + hi.weight)
        new_node.left = lo
        new_node.right = hi
        heapq.heappush(nodes, new_node)

        steps.append(("add_node", new_node))
        steps.append(("add_edge", (lo, new_node, "0")))
        steps.append(("add_edge", (hi, new_node, "1")))

        # Generate Graphviz image for the current step
        dot = graphviz.Digraph()
        added_edges = set()
        for node in sorted(nodes, key=lambda x: x.weight):
            add_node_to_graph(
                dot, node, added_edges=added_edges, total_weight=total_weight
            )
        add_node_to_graph(
            dot, new_node, added_edges=added_edges, total_weight=total_weight
        )
        try:
            dot.render(
                filename=os.path.join(output_dir, f"step_{step_count}"), format="png"
            )
        except graphviz.backend.ExecutableNotFound:
            print(
                f"Warning: Graphviz executable not found. Skipping step {step_count}."
            )
        except Exception as e:
            print(
                f"Warning: An error occurred while rendering the graph for step {step_count}: {e}"
            )
        step_count += 1

    # Final step: add codes to the nodes
    root = nodes[0]
    code_map = {}
    build_codes_recursive(root, "", code_map)

    final_dot = graphviz.Digraph()
    added_edges = set()
    add_node_to_graph(
        final_dot,
        root,
        added_edges=added_edges,
        code_map=code_map,
        total_weight=total_weight,
        final_iteration=True,
    )
    try:
        final_dot.render(
            filename=os.path.join(output_dir, f"step_{step_count}"), format="png"
        )
    except graphviz.backend.ExecutableNotFound:
        print(f"Warning: Graphviz executable not found. Skipping final step.")
    except Exception as e:
        print(f"Warning: An error occurred while rendering the final graph: {e}")
    steps.append(("final", [root]))

    return steps


def add_node_to_graph(
    dot,
    node,
    parent=None,
    edge_label=None,
    added_edges=None,
    code_map=None,
    total_weight=None,
    final_iteration=False,
):
    if node is not None:
        if node.word is not None:  # Leaf node
            code = (
                code_map[node.word]
                if final_iteration and code_map and node.word in code_map
                else ""
            )
            probability = node.weight / total_weight if total_weight else 0
            label = f"{node.word}\n{node.weight}\n{probability:.4f}"
            if final_iteration:
                label = f"{node.word}\n{code}\n{node.weight}\n{probability:.4f}"
        else:  # Non-leaf node
            probability = node.weight / total_weight if total_weight else 0
            label = f"{node.weight}\n{probability:.4f}"

        dot.node(str(id(node)), label=label)

        if parent is not None and added_edges is not None:
            edge = (str(id(parent)), str(id(node)))
            if edge not in added_edges:
                dot.edge(str(id(parent)), str(id(node)), label=edge_label)
                added_edges.add(edge)

        if added_edges is None:
            added_edges = set()

        add_node_to_graph(
            dot,
            node.left,
            parent=node,
            edge_label="0",
            added_edges=added_edges,
            code_map=code_map,
            total_weight=total_weight,
            final_iteration=final_iteration,
        )
        add_node_to_graph(
            dot,
            node.right,
            parent=node,
            edge_label="1",
            added_edges=added_edges,
            code_map=code_map,
            total_weight=total_weight,
            final_iteration=final_iteration,
        )


def build_codes_from_frequencies(frequencies):
    nodes = [
        HuffmanNode(symbol, weight, word=symbol)
        for symbol, weight in frequencies.items()
    ]
    heapq.heapify(nodes)

    while len(nodes) > 1:
        lo = heapq.heappop(nodes)
        hi = heapq.heappop(nodes)
        new_node = HuffmanNode(weight=lo.weight + hi.weight)
        new_node.left = lo
        new_node.right = hi
        heapq.heappush(nodes, new_node)

    root = nodes[0]
    code_map = {}
    build_codes_recursive(root, "", code_map)
    return code_map


def build_codes_recursive(node, code, code_map):
    if node is not None:
        if node.word is not None:
            code_map[node.word] = code
        build_codes_recursive(node.left, code + "0", code_map)
        build_codes_recursive(node.right, code + "1", code_map)


def read_file(filename, subfolder_path):
    with open(os.path.join(subfolder_path, "rgb_graphs", filename), "r") as f:
        lines = f.readlines()
        # Remove the line containing "Encoded symbols"
        lines = [line for line in lines if not line.startswith("Encoded symbols")]
        return "".join(lines)


def tuple_encode(image):
    # Example tuple encoding process
    pixels = list(image.getdata())
    frequencies = Counter(pixels)
    huffman_tree = build_huffman_tree(frequencies)
    codebook = build_codes(huffman_tree)
    encoded_image = "".join(codebook[pixel] for pixel in pixels)
    return encoded_image, huffman_tree, frequencies


def show_tuple_encoding(
    subfolder_path, image_path, stacked_widget, show_step_by_step_graph
):
    print("Loading image for tuple encoding...")
    image = Image.open(image_path).convert("RGB")

    print("Encoding image using tuple encoding...")
    encoded_image, huffman_tree, frequencies = tuple_encode(image)
    code_map = build_codes(huffman_tree)

    # Create a subfolder for tuple encoding results
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    subfolder_name = (
        f"Tuple_{timestamp}_{os.path.splitext(os.path.basename(image_path))[0]}"
    )
    subfolder_path = os.path.join(subfolder_path, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    # Save the encoded image text as a .txt file
    print("Creating text file for encoded text...")
    encoded_text_file_name = os.path.join(
        subfolder_path,
        f"Tuple_Codigo_{os.path.splitext(os.path.basename(image_path))[0]}.txt",
    )
    with open(encoded_text_file_name, "w") as f:
        f.write(encoded_image)

    # Save the Huffman tree graph
    print("Saving Huffman tree graph...")
    save_huffman_tree_graph(
        huffman_tree,
        frequencies,
        os.path.join(subfolder_path, "Tuple_Huffman_Tree"),
        code_map,
    )

    # Decode the image
    print("Decoding image...")
    decoded_pixels = tuple_huffman_decode(encoded_image, huffman_tree, image.size)
    decoded_image = Image.new("RGB", image.size)
    decoded_image.putdata(decoded_pixels)
    decoded_image.save(os.path.join(subfolder_path, "Tuple_Decoded.jpg"))

    # Calculate and display Huffman's coding efficiency
    total_pixels = image.size[0] * image.size[1]
    entropy, avg_length, efficiency = calculate_efficiency(frequencies, code_map)
    longest_code_word = max(code_map.values(), key=len)
    longest_code_word_length = len(longest_code_word)

    info = (
        f"Average length of the encoded symbols: {avg_length:.4f}\n"
        f"Entropy of the source: {entropy:.4f}\n"
        f"Huffman's coding efficiency: {efficiency:.4f}\n"
        f"Longest encoded word: {longest_code_word} (length: {longest_code_word_length})\n"
    )

    print("Tuple encoding process completed successfully.")

    # Display the results in the GraphWindow
    graph_pixmap = QPixmap(os.path.join(subfolder_path, "Tuple_Huffman_Tree.png"))
    window = GraphWindow(
        "Tuple Encoding Results",
        graph_pixmap,
        stacked_widget,
        frequencies,
        show_step_by_step_graph,
    )
    window.set_info(info)
    stacked_widget.addWidget(window)
    stacked_widget.setCurrentWidget(window)
    window.showMaximized()
    window.update()


if __name__ == "__main__":
    main()
