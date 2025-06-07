# Web-Based Facial Authentication System

      This project is a simple web app for facial recognition login and registration using Python, Flask, and OpenCV.

## Features
  
      - Register your face with a username using your webcam.
      - Log in by authenticating your face with the webcam.
      - Scanning animation appears on the webcam feed during scanning.
      - Light and dark mode toggle on all pages.
      - Works on desktop/laptop browsers with webcam support.

## How to Run

        1. **Install requirements**  
           Make sure you have Python 3.8+ installed.  
           Then install dependencies:
           ```
               pip install flask opencv-contrib-python numpy
           ```
        
        2. **Start the App**  
           ```
               python facial_auth_app.py
           ```
        
        3. **Open in Browser**  
               Go to [http://127.0.0.1:5000](http://127.0.0.1:5000)
        
        ## Usage
        
        - **Register:**  
              Click "Register Face", enter a username, and let the webcam capture your face.
        - **Authenticate:**  
              Click "Authenticate (Login)" and look at the webcam. If your face matches a registered user, you will be logged in.
        - **Theme:**  
              Use the ☀️ button in the corner to switch between light and dark mode.

## Notes

      - Your webcam must be enabled for this app to work.
      - This app is for demonstration/learning purposes only, not for production security.
      - Only one face should be visible during registration and login.

## Credits

        - Made by DY MANASA
        - Uses [Flask](https://flask.palletsprojects.com/) and [OpenCV](https://opencv.org/)
