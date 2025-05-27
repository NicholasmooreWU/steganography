from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import numpy as np
from PIL import Image
import os

def aes_encrypt(plain_text, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
    iv = cipher.iv
    return iv, ct_bytes

def aes_decrypt(iv, ct_bytes, key):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct_bytes), AES.block_size)
    return pt.decode()

def string_to_binary(data):
    return ''.join(format(byte, '08b') for byte in data)

def binary_to_string(binary_data):
    byte_array = bytearray()
    for i in range(0, len(binary_data), 8):
        byte_array.append(int(binary_data[i:i+8], 2))
    return bytes(byte_array)

def alter_image(image_path, binary_data):
    image = Image.open(image_path)
    data = np.array(image, dtype=np.uint8)

    binary_index = 0
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            for k in range(data.shape[2]):
                if binary_index < len(binary_data):
                    bit = int(binary_data[binary_index])
                    if bit not in (0, 1):
                        raise ValueError("Binary data must only contain 0s and 1s")
                    data[y, x, k] = (data[y, x, k] & ~1) | bit
                    binary_index += 1
                else:
                    break
            if binary_index >= len(binary_data):
                break
        if binary_index >= len(binary_data):
            break

    new_image = Image.fromarray(data)
    new_image_path = os.path.splitext(image_path)[0] + "_altered.png"
    new_image.save(new_image_path)
    return new_image_path

def lsb_extract(image_path, data_length):
    img = Image.open(image_path)
    img = img.convert('RGB')
    data = np.array(img)
    binary_data = ''
    binary_index = 0
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(3):  
                if binary_index < data_length:
                    binary_data += str(data[i, j, k] & 1)
                    binary_index += 1
    return binary_data

def main():
    image_path = os.path.abspath(r"C:\Users\nomoo\Downloads\CS 351 Project\test_image.png")
    plain_text = "Hello, World!"
    key = get_random_bytes(16) 

    iv, ct_bytes = aes_encrypt(plain_text, key)
    print(f"Ciphertext: {ct_bytes}")

    binary_data = string_to_binary(ct_bytes)
    new_image_path = alter_image(image_path, binary_data)
    print(f"New image with LSB data saved at: {new_image_path}")

    decrypted_text = aes_decrypt(iv, ct_bytes, key)
    print(f"Decrypted text: {decrypted_text}")

if __name__ == "__main__":
    main()