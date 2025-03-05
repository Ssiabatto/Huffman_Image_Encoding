# Huffman RGB Project

This project implements Huffman coding to encode and decode the RGB channels of an image separately, as well as encoding and decoding the image as tuples. It visualizes each channel and the corresponding Huffman trees built during the encoding process. The main goal is to demonstrate the efficiency of Huffman coding in image compression and restoration.

## Project Structure

```
huffman_rgb_project
├── src
│   ├── main.py          # Entry point of the application
│   ├── huffman.py       # Implementation of Huffman coding
│   ├── utils.py         # Utility functions for image processing
│   └── visualization.py  # Visualization of RGB channels and Huffman trees
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <https://github.com/Ssiabatto/Huffman_Image_Encoding.git>
   cd huffman_rgb_project
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Place the image you want to encode in the project directory.
2. Run the application:
   ```
   python src/main.py
   ```

3. Follow the prompts to select the image and view the results.

## Functionality

- **Encoding and Decoding RGB Channels**: The application encodes each RGB channel of the image using Huffman coding and decodes them back to restore the original image.
- **Encoding and Decoding Tuples**: The application also supports encoding and decoding tuples using Huffman coding.
- **Visualization**: It visualizes the individual RGB channels and the corresponding Huffman trees, providing insights into the encoding process.
- **Image Processing**: Utility functions are included to handle image splitting and merging.

## Dependencies

- Pillow: For image processing tasks.
- Matplotlib or Graphviz: For visualizing the Huffman trees and images.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.