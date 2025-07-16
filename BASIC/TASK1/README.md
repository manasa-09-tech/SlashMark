🔐 Text Encryption Web App

This is a basic web app that lets you encrypt and decrypt text using a secret key.
It's a beginner-friendly project made with Node.js.


---

📁 Files in This Project

        app.js – Main code that runs the server and handles encryption/decryption.

        .env – Stores your secret key (don’t share this file!).



---

🚀 How to Run the Project

  1. Clone the project or download the folder.


  2. Open a terminal in the project folder.


  3. Install required packages by running:
     

      npm init -y
      npm install express
      npm install
      npm install dotenv


  5. Create a .env file and add your encryption key like this:

      ENCRYPTION_KEY=12345678901234567890123456789012


  6. Start the server with:

      nodemon app.js


  7. Open your browser and go to:

      http://localhost:3000/encrypt




---

✨ What It Does

         Lets you type a message and encrypt it.

        You can also decrypt any message if you have the same secret key.

        Uses basic cryptography methods.



---

📌 Notes

Make sure your .env file is not shared with anyone.

This project is for learning purposes.



---

📄 License

Free to use. No license restrictions.
