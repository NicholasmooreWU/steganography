# Secure Image Steganography with Encryption

## ⚠️ Security Disclaimer (Important)

This project is intended **strictly for educational and research purposes**.

- This implementation has **not been security audited**
- It is **not designed, tested, or reviewed for production use**
- It should **not be used to protect sensitive, personal, or confidential information**
- No guarantees are made regarding the security, correctness, or robustness of this system

If you require secure communication or data protection, use well-established,
professionally maintained cryptographic tools and libraries.

By using this code, you acknowledge that you do so **at your own risk**.

---

## Overview

This project implements a Python-based steganography system that embeds
**encrypted text messages inside image files** using Least Significant Bit (LSB)
encoding. The project explores how data can be transformed, encoded, hidden, and
recovered while maintaining data integrity.

It combines **encryption**, **binary data encoding**, and **image manipulation**
to demonstrate secure data handling concepts relevant to privacy-aware systems,
data validation pipelines, and information security fundamentals.

This project is an **educational exploration** of steganography and cryptography
principles and is **not intended for real-world secure communication**.

---

## Key Features

- Encrypts messages before embedding them into images
- Uses Least Significant Bit (LSB) manipulation of RGB pixel values
- Preserves image usability while altering pixel-level data
- Supports full message recovery and verification
- Measures execution time for encoding and decoding operations

---

## Encryption Approach

The primary encryption method implemented in this project is **ChaCha20**, an
industry-grade stream cipher.

Encryption details:
- Password-based key derivation using PBKDF2 with SHA-256
- Randomly generated salt and nonce for each encryption
- Base64 encoding for safe binary conversion and storage

Encrypted messages are converted into binary before being embedded into an image
pixel data.

---

## How the Steganography Works

1. **Message Encryption**
   - User-provided text is encrypted using ChaCha20
   - A random salt and nonce are generated
   - The encrypted message is base64-encoded

2. **Binary Encoding**
   - The encrypted text is converted into an 8-bit binary string
   - A delimiter is appended to indicate the end of the message

3. **Image Modification**
   - Each bit of the binary message is embedded into the least significant bit
     of RGB pixel values
   - Pixels are modified sequentially until the full message is encoded

4. **Message Extraction**
   - LSB values are read from the altered image
   - Binary data is reconstructed and converted back to text
   - The encrypted message is recovered and decoded

---

## Technologies Used

- Python
- Pillow (PIL) for image processing
- cryptography library (ChaCha20, PBKDF2, SHA-256)
- Base64 encoding
- OS and file system utilities

---

## How to Run

### Requirements

Install required dependencies:

```bash
pip install pillow cryptography
