from PIL import Image
import os
import base64
import getpass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import time
import argparse
import logging


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain a digit.")
    if not any(c.isalpha() for c in password):
        raise ValueError("Password must contain a letter.")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler()],
    )
    parser = argparse.ArgumentParser(
        description="Steganography with ChaCha20 encryption."
    )
    subparsers = parser.add_subparsers(dest="command")

    encode_parser = subparsers.add_parser(
        "encode", help="Encode a message into an image."
    )
    encode_parser.add_argument("--image", required=True, help="Path to input image.")
    encode_parser.add_argument("--message", required=True, help="Message to encode.")
    encode_parser.add_argument(
        "--output", required=False, help="Path to save altered image."
    )
    encode_parser.add_argument(
        "--password", required=False, help="Password for encryption."
    )

    decode_parser = subparsers.add_parser(
        "decode", help="Decode a message from an image."
    )
    decode_parser.add_argument("--image", required=True, help="Path to altered image.")
    decode_parser.add_argument(
        "--password", required=False, help="Password for decryption."
    )

    args = parser.parse_args()

    if args.command == "encode":
        password = args.password or getpass.getpass("Enter encryption password: ")
        try:
            validate_password(password)
            if len(password) < 12:
                logging.warning(
                    "Password is valid but less than 12 characters. "
                    "Consider using a stronger password."
                )
            start_time = time.time()
            enc = Encoder(args.message, args.image)
            encrypted_message = enc.text_encoder(enc.msg, password)
            binary_message = enc.text_to_binary(encrypted_message)
            altered_image_path = enc.alter_image(
                enc.img,
                binary_message,
                args.output,
                None,
            )
            end_time = time.time()
            elapsed = end_time - start_time
            logging.info("Altered image saved at: %s", altered_image_path)
            logging.info("Encoded message: %s", encrypted_message)
            logging.info("Encoding time: %.2f seconds", elapsed)
        except FileNotFoundError:
            logging.error("Input image file not found.")
        except ValueError as ve:
            logging.error(f"Password validation error: {ve}")
        except Exception as e:
            logging.exception(f"Unexpected error during encoding: {e}")

    elif args.command == "decode":
        password = args.password or getpass.getpass("Enter decryption password: ")
        try:
            validate_password(password)
            if len(password) < 12:
                logging.warning(
                    "Password is valid but less than 12 characters. "
                    "Consider using a stronger password."
                )
            start_time = time.time()
            decoder = Decoder(args.image)
            binary_message = decoder.binary_from_image(decoder.img)
            decoded_message = decoder.binary_to_text(binary_message)
            end_time = time.time()
            elapsed = end_time - start_time
            logging.info("Decoded message: %s", decoded_message)
            logging.info("Decoding time: %.2f seconds", elapsed)
        except FileNotFoundError:
            logging.error("Altered image file not found.")
        except ValueError as ve:
            logging.error(f"Password validation error: {ve}")
        except Exception as e:
            logging.exception(f"Unexpected error during decoding: {e}")

    else:
        parser.print_help()


# Encoder class
class Encoder:
    """
    Class for encoding messages in images using ChaCha20.
    Supports flexible image formats.
    """

    def __init__(self, message, image_path):
        """
        Initialize Encoder.
        Args:
            message (str): The message to encode.
            image_path (str): Path to the image file.
        """
        self.msg = message
        self.img = Image.open(image_path)
        self.image_path = image_path

    def text_encoder(self, text, key):
        """
        Encrypt text using ChaCha20.
        Args:
            text (str): Text to encrypt.
            key (str): Encryption key.
        Returns:
            str: Encrypted text (base64).
        """
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key_bytes = kdf.derive(key.encode())
        nonce = os.urandom(16)
        algorithm = algorithms.ChaCha20(key_bytes, nonce)
        cipher = Cipher(algorithm, mode=None)
        encryptor = cipher.encryptor()
        ct = encryptor.update(text.encode()) + encryptor.finalize()
        return base64.urlsafe_b64encode(salt + nonce + ct).decode()

    def text_to_binary(self, text):
        """
        Convert text to binary string.
        Args:
            text (str): Text to convert.
        Returns:
            str: Binary string.
        """
        return "".join(format(ord(c), "08b") for c in text)

    def alter_image(
        self,
        img,
        binary_message,
        output_path=None,
        output_format=None,
    ):
        """
        Embed binary message into image and save in specified format.
        Args:
            img (PIL.Image): Image object.
            binary_message (str): Binary message to embed.
            output_path (str): Path to save altered image.
            output_format (str): Image format (PNG, JPEG, BMP, etc.).
        Returns:
            str: Path to saved image.
        """
        pixels = img.load()
        width, height = img.size
        binary_message += "1111111111111110"
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
        if not output_path:
            output_path = os.path.splitext(self.image_path)[0] + "_altered"
            if output_format:
                output_path += f".{output_format.lower()}"
            else:
                output_path += ".png"
        img.save(output_path, format=output_format if output_format else "PNG")
        return output_path


# Decoder class
class Decoder:
    """
    Class for extracting and decoding messages from images using ChaCha20.
    """

    def __init__(self, image_path):
        """
        Initialize Decoder.
        Args:
            image_path (str): Path to the image file.
        """
        self.img = Image.open(image_path)
        self.image_path = image_path

    def binary_from_image(self, img):
        """
        Extract binary message from image.
        Args:
            img (PIL.Image): Image object.
        Returns:
            str: Binary message.
        """
        pixels = img.load()
        width, height = img.size
        binary_message = ""
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                binary_message += str(r & 1)
                binary_message += str(g & 1)
                binary_message += str(b & 1)
        binary_message = binary_message.split("1111111111111110")[0]
        return binary_message

    def binary_to_text(self, binary):
        """
        Convert binary string to text.
        Args:
            binary (str): Binary string.
        Returns:
            str: Decoded text.
        """
        return "".join(chr(int(binary[i : i + 8], 2)) for i in range(0, len(binary), 8))


if __name__ == "__main__":
    main()