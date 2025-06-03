🛡 Image Encryption & Decryption Tool

A simple Node.js project that securely encrypts and decrypts image files using a generated key. Ideal for beginners learning about basic cryptography and file protection.


---

📂 Project Structure

      imcrypt-main/
      │
      ├── node_modules/            # Node.js dependencies
      ├── utils/                   # Utility functions for encryption/decryption
      │
      ├── dist/                    # Output folder for encrypted/decrypted images (create manually)
      │
      ├── index.js                 # Main script
      ├── nmap.png                 # Sample image (input)
      │
      ├── .gitignore               # Files to ignore in Git
      ├── .prettierrc.json         # Code formatting config
      │
      ├── LICENSE                  # License information
      ├── package.json             # Project metadata and dependencies
      ├── package-lock.json        # Exact dependency versions
      └── README.md                # You're reading it!
      

---

🚀 How to Run

      1. Install Node.js & Dependencies
      
            npm install
      
      2. Encrypt an Image
      
            node index.js -e nmap.png
      
      ➡ Outputs:
      
            nmap_encrypted.png in dist/
      
            nmap_key.txt in dist/
      
      
      3. Decrypt the Image
      
            node index.js -d dist/nmap_encrypted.png -k dist/nmap_key.txt
      
      ➡ Outputs:

            decrypted_nmap.png in dist/



---

💡 Features

          Encrypts image files to prevent unauthorized viewing.
          
          Generates a secure key for decryption.
          
          Decrypts only if the correct key is provided.



---

📚 Learnings

          Basic cryptography using Node.js
          
          File system operations
          
          Secure handling of image files
---
👤 Author

        Made by D V Manasa
        As part of a Cybersecurity Internship at SlashMark, 2025.

