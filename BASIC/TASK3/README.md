# Image Encryption and Decryption GUI

    A simple Python GUI application that lets you encrypt and decrypt image files using strong symmetric encryption (Fernet).
    Even if someone accesses your encrypted images, they cannot decrypt them without your secret key.

## Features

      - **Encrypt** any image file with a secure key.
      - **Decrypt** encrypted images using the same key.
      - **Generate and manage secret keys**.
      - **Preview** the decrypted image directly in the GUI.
      - **User-friendly interface** with Tkinter.

## Requirements

      - Python 3.x
      - [cryptography](https://pypi.org/project/cryptography/)
      - [Pillow](https://pypi.org/project/Pillow/) (for image preview)

Install dependencies with:

      ```bash
      pip install cryptography pillow
      ```

## Usage

      1. **Run the application:**
          ```bash
          python image_crypto_gui.py
          ```
      
      2. **Generate a Key:**
          - Click “Generate Key” to create a secret key file (e.g., `key.key`).  
            **Keep this file safe! Anyone with it can decrypt your images.**
      
      3. **Encrypt an Image:**
          - Click **Browse** next to “Input File” and select your image.
          - Click **Browse** next to “Save As” and choose where to save the encrypted file.
          - Make sure the correct key file is shown.
          - Click **Encrypt**.
      
      4. **Decrypt an Image:**
          - Click **Browse** next to “Input File” and select the encrypted file.
          - Click **Browse** next to “Save As” and choose where to save the decrypted image.
          - Make sure the correct key file is shown.
          - Click **Decrypt**.
          - **After decrypting, the image will be previewed in a popup window.**

## Security Notes

      - **Keep your key file secure.** Anyone who gets it can decrypt your images.
      - The encrypted files can be safely shared—only someone with the key can decrypt them.

## License

This project is for educational purposes. Use at your own risk.

---

**Enjoy encrypting your images securely!**
