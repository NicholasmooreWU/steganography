from PIL import Image
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import time

class Encoder:
    def __init__(self, message, image_path):
        self.msg = message
        self.img = Image.open(image_path)
        self.image_path = image_path

    def text_encoder(self, text, key):
        # ChaCha20 encryption
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(key.encode())
        nonce = os.urandom(16)
        algorithm = algorithms.ChaCha20(key, nonce)
        cipher = Cipher(algorithm, mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(text.encode()) + encryptor.finalize()
        return base64.urlsafe_b64encode(salt + nonce + ct).decode()

    def text_to_binary(self, text):
        return ''.join(format(ord(c), '08b') for c in text)

    def binary_to_text(self, binary):
        text = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
        return text

    def alter_image(self, img, binary_message):
        pixels = img.load()
        width, height = img.size
        binary_message += '1111111111111110'  
        data_index = 0
        for y in range(height):
            for x in range(width):
                if data_index < len(binary_message):
                    r, g, b = pixels[x, y]
                    r = (r & ~1) | int(binary_message[data_index])
                    data_index += 1
                    if data_index < len(binary_message):
                        g = (g & ~1) | int(binary_message[data_index])
                        data_index += 1
                    if data_index < len(binary_message):
                        b = (b & ~1) | int(binary_message[data_index])
                        data_index += 1
                    pixels[x, y] = (r, g, b)
                else:
                    break
            if data_index >= len(binary_message):
                break

        new_image_path = os.path.splitext(self.image_path)[0] + "_altered.png"
        img.save(new_image_path)
        return new_image_path

    def binary_from_image(self, img):
        pixels = img.load()
        width, height = img.size
        binary_message = ""

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                binary_message += str(r & 1)
                binary_message += str(g & 1)
                binary_message += str(b & 1)

        binary_message = binary_message.split('1111111111111110')[0]
        return binary_message
    def binary_to_text(self, binary_data):
        text = ""
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            text += chr(int(byte, 2))
        return text

image_path = os.path.abspath(r"C:\Users\nomoo\Downloads\CS 351 Project\test_image.png")
encoded_message = "Hello, World!"
start_time=time.time()
enc = Encoder(encoded_message, image_path)
encrypted_message = enc.text_encoder(enc.msg, "password123")
binary_message = enc.text_to_binary(encrypted_message)
altered_image_path = enc.alter_image(enc.img, binary_message)

print(f"Altered image saved at: {altered_image_path}")
print(f"Encoded message: {encrypted_message}")
print(f"Binary string: {binary_message}")

altered_img = Image.open(altered_image_path)
decoded_binary_message = enc.binary_from_image(altered_img)
decoded_message = enc.binary_to_text(decoded_binary_message)
end_time=time.time()
print(f"Decoded binary string: {decoded_binary_message}")
print(f"Decoded message: {decoded_message}")
print("Time taken:", end_time-start_time)