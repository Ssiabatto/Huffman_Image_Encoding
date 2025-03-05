import heapq
from collections import Counter
from PIL import Image
import math


class HuffmanNode:
    def __init__(self, symbol=None, weight=0, word=None, left=None, right=None):
        self.symbol = symbol
        self.weight = weight
        self.word = word
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.weight < other.weight


def build_huffman_tree(frequencies):
    heap = [HuffmanNode(sym, freq) for sym, freq in frequencies.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(weight=left.weight + right.weight, left=left, right=right)
        heapq.heappush(heap, merged)
    return heap[0]


def build_codes(node, code="", code_map={}):
    if node.symbol is not None:
        code_map[node.symbol] = code
    else:
        build_codes(node.left, code + "0", code_map)
        build_codes(node.right, code + "1", code_map)
    return code_map


def huffman_encode(data):
    # Calculate frequency of each symbol in the data
    frequencies = Counter(data)

    # Create a priority queue to hold the nodes
    priority_queue = [
        HuffmanNode(symbol, weight) for symbol, weight in frequencies.items()
    ]
    heapq.heapify(priority_queue)

    steps = []

    while len(priority_queue) > 1:
        # Pop two nodes with the lowest frequency
        lo = heapq.heappop(priority_queue)
        hi = heapq.heappop(priority_queue)

        # Merge the two nodes
        new_node = HuffmanNode(weight=lo.weight + hi.weight)
        new_node.left = lo
        new_node.right = hi
        heapq.heappush(priority_queue, new_node)

        # Record the steps
        steps.append(("add_node", new_node))
        steps.append(("add_edge", (lo, new_node)))
        steps.append(("add_edge", (hi, new_node)))

    # The remaining node is the root of the Huffman tree
    huffman_tree = heapq.heappop(priority_queue)

    # Generate the Huffman codes
    huffman_codes = build_codes(huffman_tree)

    # Encode the data
    encoded_data = "".join(huffman_codes[symbol] for symbol in data)
    print(f"Encoded data length: {len(encoded_data)}")  # Debugging information

    return huffman_codes, huffman_tree, frequencies, steps, encoded_data


def huffman_decode(encoded_data, huffman_tree, image_size):
    decoded_pixels = []
    node = huffman_tree
    for bit in encoded_data:
        if bit == "0":
            node = node.left
        else:
            node = node.right

        if node.symbol is not None:
            decoded_pixels.append(node.symbol)
            node = huffman_tree

    expected_size = image_size[0] * image_size[1]
    decoded_size = len(decoded_pixels)
    if decoded_size != expected_size:
        print(f"Expected size: {expected_size}, Decoded size: {decoded_size}")
        print(f"Encoded data length: {len(encoded_data)}")
        print(
            f"Decoded pixels: {decoded_pixels[:100]}"
        )  # Print first 100 decoded pixels for debugging
        print(
            f"Decoded pixels (last 100): {decoded_pixels[-100:]}"
        )  # Print last 100 decoded pixels for debugging
        raise ValueError("Decoded data does not match the expected image size")

    decoded_image = Image.new("L", image_size)
    decoded_image.putdata(decoded_pixels)
    return decoded_image


def tuple_huffman_decode(encoded_data, huffman_tree, image_size):
    decoded_pixels = []
    node = huffman_tree
    for bit in encoded_data:
        if bit == "0":
            node = node.left
        else:
            node = node.right

        if node.symbol is not None:
            decoded_pixels.append(node.symbol)
            node = huffman_tree

    expected_size = image_size[0] * image_size[1]
    decoded_size = len(decoded_pixels)
    if decoded_size != expected_size:
        print(f"Expected size: {expected_size}, Decoded size: {decoded_size}")
        print(f"Encoded data length: {len(encoded_data)}")
        print(
            f"Decoded pixels: {decoded_pixels[:100]}"
        )  # Print first 100 decoded pixels for debugging
        print(
            f"Decoded pixels (last 100): {decoded_pixels[-100:]}"
        )  # Print last 100 decoded pixels for debugging
        raise ValueError("Decoded data does not match the expected image size")

    return decoded_pixels


def calculate_entropy(frequencies, total_symbols):
    entropy = 0
    for symbol, freq in frequencies.items():
        prob = freq / total_symbols
        entropy_contribution = -prob * math.log2(prob)
        entropy += entropy_contribution
    return entropy


def calculate_average_length(code_map, frequencies, total_symbols):
    avg_length = 0
    for symbol, code in code_map.items():
        if symbol in frequencies:
            prob = frequencies[symbol] / total_symbols
            length_contribution = prob * len(code)
            avg_length += length_contribution
    return avg_length


def calculate_efficiency(frequencies, code_map):
    total_symbols = sum(frequencies.values())
    entropy = calculate_entropy(frequencies, total_symbols)
    avg_length = calculate_average_length(code_map, frequencies, total_symbols)
    efficiency = entropy / avg_length if avg_length != 0 else 0
    return entropy, avg_length, efficiency
