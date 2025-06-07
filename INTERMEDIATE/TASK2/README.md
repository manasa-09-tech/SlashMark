# Secure Credit Card Vault (Local)

    A simple and beautiful web app for securely encrypting and storing credit card numbers **locally** (no paid cloud required).  
    Built with Flask and AES-256 encryption. Great for demos, learning, and local secure storage

---

## Features

    - **AES-256 encryption** for credit card numbers
    - **Local secure storage** (`cards.json` file, no cloud or AWS needed)
    - **Modern, mobile-friendly web UI**
    - **Admin token access control**
    - **Beautiful design & icons**

---

## How to Run
    
    1. **Install dependencies:**
        ```bash
        pip install flask pycryptodome
        ```
    
    2. **(Optional) Set environment variables:**
        - `ENCRYPTION_KEY_BASE64` (32-byte base64 key, auto-generated if not set)
        - `ADMIN_TOKEN` (default: `supersecrettoken`)
        - `FLASK_SECRET_KEY` (for Flask session, any random string)
    
    3. **Start the app:**
        ```bash
        python credit_card_webapp_local.py
        ```
    
    4. **Visit** [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

    - **Encrypt & Store Card:**  
      Enter Admin Token, Card ID, and Card Number. Click "Encrypt & Store".
    - **Decrypt Card:**  
      Enter Admin Token and Card ID. Click "Decrypt" to view the decrypted card number.

---

## Security Notes

  - Data is encrypted with AES-256 before saving to `cards.json`.
  - Change the admin token for your own use.
  - For demo/learning only; do not use for sensitive personal data in production.

---

## License

  MIT License

---
