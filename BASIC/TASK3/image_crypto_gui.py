import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
from PIL import Image, ImageTk
import os

class ImageCryptoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Encryption/Decryption")
        self.key_file = "key.key"
        self.file_path = tk.StringVar()
        self.save_path = tk.StringVar()
        self.image_label = None  # For displaying image

        tk.Label(root, text="Input File:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.file_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(root, text="Save As:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.save_path, width=40).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.save_file).grid(row=1, column=2, padx=5, pady=5)

        tk.Button(root, text="Generate Key", command=self.generate_key).grid(row=2, column=0, padx=5, pady=10)
        tk.Button(root, text="Encrypt", command=self.encrypt_image).grid(row=2, column=1, padx=5, pady=10)
        tk.Button(root, text="Decrypt", command=self.decrypt_image).grid(row=2, column=2, padx=5, pady=10)

        tk.Label(root, text="Key file:").grid(row=3, column=0, padx=5, pady=5)
        self.key_path_entry = tk.Entry(root, width=40)
        self.key_path_entry.insert(0, self.key_file)
        self.key_path_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse", command=self.browse_key).grid(row=3, column=2, padx=5, pady=5)

    def browse_file(self):
        path = filedialog.askopenfilename(title="Select file")
        if path:
            self.file_path.set(path)

    def save_file(self):
        path = filedialog.asksaveasfilename(title="Save file as")
        if path:
            self.save_path.set(path)

    def browse_key(self):
        path = filedialog.askopenfilename(title="Select key file", filetypes=[("Key Files", "*.key"), ("All Files", "*.*")])
        if path:
            self.key_path_entry.delete(0, tk.END)
            self.key_path_entry.insert(0, path)

    def generate_key(self):
        key_path = self.key_path_entry.get()
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
        messagebox.showinfo("Success", f"Key file generated: {key_path}")

    def load_key(self):
        key_path = self.key_path_entry.get()
        if not os.path.exists(key_path):
            messagebox.showerror("Error", f"Key file not found: {key_path}")
            return None
        with open(key_path, 'rb') as f:
            return f.read()

    def encrypt_image(self):
        key = self.load_key()
        if not key:
            return
        if not self.file_path.get() or not self.save_path.get():
            messagebox.showerror("Error", "Specify input and output files.")
            return
        fernet = Fernet(key)
        try:
            with open(self.file_path.get(), 'rb') as file:
                original = file.read()
            encrypted = fernet.encrypt(original)
            with open(self.save_path.get(), 'wb') as enc_file:
                enc_file.write(encrypted)
            messagebox.showinfo("Success", f"Image encrypted and saved to {self.save_path.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {e}")

    def decrypt_image(self):
        key = self.load_key()
        if not key:
            return
        if not self.file_path.get() or not self.save_path.get():
            messagebox.showerror("Error", "Specify input and output files.")
            return
        fernet = Fernet(key)
        try:
            with open(self.file_path.get(), 'rb') as enc_file:
                encrypted = enc_file.read()
            decrypted = fernet.decrypt(encrypted)
            with open(self.save_path.get(), 'wb') as dec_file:
                dec_file.write(decrypted)
            messagebox.showinfo("Success", f"Image decrypted and saved to {self.save_path.get()}")
            self.show_image(self.save_path.get())
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {e}")

    def show_image(self, path):
        top = tk.Toplevel(self.root)
        top.title("Decrypted Image Preview")
        try:
            img = Image.open(path)
            img.thumbnail((500, 500))  # Resize for preview
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(top, image=photo)
            label.image = photo  # Keep reference
            label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {e}")

if __name__ == "__main__":
    # Make sure Pillow is installed: pip install pillow
    root = tk.Tk()
    app = ImageCryptoGUI(root)
    root.mainloop()