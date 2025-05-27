from PIL import Image
import time

def caesar_cipher_encode(text, shift):
    encoded = ""
    for char in text:
        if char.isalpha():
            shift_amount = shift % 26
            if char.islower():
                encoded += chr((ord(char) - ord('a') + shift_amount) % 26 + ord('a'))
            else:
                encoded += chr((ord(char) - ord('A') + shift_amount) % 26 + ord('A'))
        else:
            encoded += char
    binary_data = ''.join(format(ord(i), '08b') for i in encoded)
    length = format(len(binary_data), '032b') 
    return length + binary_data

def embed_binary_in_image(image_path, binary_data, output_path):
    img = Image.open(image_path)
    pixels = img.load()
    
    binary_index = 0
    for y in range(img.height):
        for x in range(img.width):
            if binary_index < len(binary_data):
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_data[binary_index])
                binary_index += 1
                if binary_index < len(binary_data):
                    g = (g & ~1) | int(binary_data[binary_index])
                    binary_index += 1
                if binary_index < len(binary_data):
                    b = (b & ~1) | int(binary_data[binary_index])
                    binary_index += 1
                pixels[x, y] = (r, g, b)
            else:
                break
    img.save(output_path)

def extract_binary_from_image(image_path):
    img = Image.open(image_path)
    pixels = img.load()
    
    binary_data = ""
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)
    
    length = int(binary_data[:32], 2)
    return binary_data[32:32+length]

def binary_to_text(binary_data):
    text = ""
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        text += chr(int(byte, 2))
    return text

def caesar_cipher_decode(encoded_text, shift):
    decoded = ""
    for char in encoded_text:
        if char.isalpha():
            shift_amount = shift % 26
            if char.islower():
                decoded += chr((ord(char) - ord('a') - shift_amount) % 26 + ord('a'))
            else:
                decoded += chr((ord(char) - ord('A') - shift_amount) % 26 + ord('A'))
        else:
            decoded += char
    return decoded

# Encode message
message = "Hello, World!"
shift = 3
start_time=time.time()
binary_data = caesar_cipher_encode(message, shift)

# Embed binary data into image
image_path = r"C:\Users\nomoo\Downloads\CS 351 Project\test_image.png"
output_path = r"C:\Users\nomoo\Downloads\CS 351 Project\encoded_image.png"
embed_binary_in_image(image_path, binary_data, output_path)

# Extract binary data from image
extracted_binary_data = extract_binary_from_image(output_path)

# Decode message
extracted_text = binary_to_text(extracted_binary_data)
decoded_message = caesar_cipher_decode(extracted_text, shift)
end_time=time.time()
print("Original Message:", message)
print("Decoded Message:", decoded_message)
print("Time taken: ",end_time-start_time)