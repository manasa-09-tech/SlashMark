# Modern Flask Authentication System

    A simple, modern, and secure authentication web application built with **Flask** and **SQLite**.

---

## Features

    - User registration with email verification
    - Secure login and logout
    - Password reset via email
    - Profile page with:
      - Email and password change
      - Profile picture upload and removal
    - Custom 404 Not Found page
    - Responsive and modern UI with dark mode

---

## How to Run

1. **Install requirements**  
   Open your terminal and run:
   ```bash
   pip install flask flask_sqlalchemy flask_login flask_wtf wtforms
   ```

2. **Start the app**  
   ```bash
   python final.py
   ```

3. **Open in your browser**  
   Visit [http://localhost:5000](http://localhost:5000)

---

## Notes

    - Simulated emails: When registering or resetting a password, the "email" will be printed in the terminal (not actually sent).
    - Profile pictures are stored in the `uploads/` folder.
    - To reset the database, simply delete the `users.db` file.
    
    ---

## Credits

    - Developed by DY MANASA

---
