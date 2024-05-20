import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import numpy as np
import random
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def convert_to_png(image_path):
    image = Image.open(image_path)
    png_image_path = os.path.splitext(image_path)[0] + ".png"
    image.save(png_image_path, "PNG")
    return png_image_path

def randomize_pixels(image_path, seed):
    # Load the image
    image = Image.open(image_path)
    image_array = np.array(image)

    # Get image dimensions
    height, width, channels = image_array.shape

    # Create a list of all pixel positions
    indices = list(np.ndindex(height, width))

    # Seed the random number generator
    random.seed(seed)

    # Shuffle the indices
    shuffled_indices = indices.copy()
    random.shuffle(shuffled_indices)

    # Create an array to hold the shuffled image
    shuffled_image_array = np.zeros_like(image_array)

    # Map the original pixels to the new shuffled positions
    for (original_index, shuffled_index) in zip(indices, shuffled_indices):
        shuffled_image_array[shuffled_index] = image_array[original_index]

    # Create the shuffled image
    shuffled_image = Image.fromarray(shuffled_image_array)
    return shuffled_image

def reverse_randomize_pixels(image, seed):
    # Convert PIL image to numpy array
    shuffled_image_array = np.array(image)

    # Get image dimensions
    height, width, channels = shuffled_image_array.shape

    # Create a list of all pixel positions
    indices = list(np.ndindex(height, width))

    # Seed the random number generator
    random.seed(seed)

    # Shuffle the indices to match the randomization step
    shuffled_indices = indices.copy()
    random.shuffle(shuffled_indices)

    # Create an array to hold the unshuffled image
    unshuffled_image_array = np.zeros_like(shuffled_image_array)

    # Map the shuffled pixels back to the original positions
    for (original_index, shuffled_index) in zip(indices, shuffled_indices):
        unshuffled_image_array[original_index] = shuffled_image_array[shuffled_index]

    # Create the unshuffled image
    unshuffled_image = Image.fromarray(unshuffled_image_array)
    return unshuffled_image

def get_unique_filename(base_path, suffix, extension):
    counter = 1
    unique_path = f"{base_path}_{suffix}{extension}"
    while os.path.exists(unique_path):
        unique_path = f"{base_path}_{suffix}_{counter}{extension}"
        counter += 1
    return unique_path

def enlarge_image(image):
    top = tk.Toplevel()
    top.title("Image Viewer")
    top.geometry("800x800")
    img = ImageTk.PhotoImage(image)
    lbl = tk.Label(top, image=img)
    lbl.image = img  # Keep a reference to prevent garbage collection
    lbl.pack(expand=True, fill=tk.BOTH)

def main():
    root = TkinterDnD.Tk()
    icon_path = resource_path('icon.ico')
    root.iconbitmap(icon_path)
    root.title("ConfidSnap")
    root.geometry("1000x720")
    root.configure(bg="white")  # Set the background color to white
    root.resizable(False, False)  # Disable window resizing

    style = ttk.Style()
    style.configure("TFrame", background="white")
    style.configure("TLabel", background="white", font=("Helvetica", 24))
    style.configure("TEntry", background="white", font=("Helvetica", 24), padding=(10, 10))
    style.configure("TButton", font=("Helvetica", 24))
    style.configure("TButton.Save.TButton", font=("Helvetica", 24), foreground="black", background="#A9A9A9", padding=(10, 10))
    style.map("TButton.Save.TButton",
              background=[("active", "#A9A9A9")])
    style.configure("TButton.Clear.TButton", font=("Helvetica", 24), foreground="black", background="#A9A9A9", padding=(10, 10))
    style.map("TButton.Clear.TButton",
              background=[("active", "#A9A9A9")])

    global processed_image
    global original_image
    global original_image_path
    global is_shuffled

    processed_image = None
    original_image = None
    original_image_path = None
    is_shuffled = False

    def on_entry_click(event):
        if code_entry.get() == 'Enter secret code':
            code_entry.delete(0, "end")  # delete all the text in the entry
            code_entry.config(foreground='black')
    def on_focusout(event):
        if code_entry.get() == '':
            code_entry.insert(0, 'Enter secret code')
            code_entry.config(foreground='gray')

    def on_drop(event, label):
        image_path = event.data
        image_path = image_path.strip('{}')  # Remove curly braces if they exist
        if image_path.lower().endswith(('.jpg', '.jpeg')):
            image_path = convert_to_png(image_path)
            temp_png_created = True
        else:
            temp_png_created = False

        upload_label.config(text="Processing...")
        root.update_idletasks()

        seed = code_entry.get()
        if not seed:
            seed = 0
        else:
            try:
                seed = int(seed)
            except ValueError:
                seed = 0  # Default to 0 if the seed is not an integer

        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)

        global processed_image
        global original_image
        global original_image_path
        global is_shuffled

        original_image_path = image_path
        original_image = Image.open(image_path)

        if label == hide_box:
            processed_image = randomize_pixels(image_path, seed)
            is_shuffled = True
            load_image_thumbnail(processed_image, reveal_box)
            load_image_thumbnail(original_image, hide_box)  # Ensure the original image stays in the hide_box
        elif label == reveal_box:
            processed_image = reverse_randomize_pixels(original_image, seed)
            is_shuffled = False
            load_image_thumbnail(processed_image, hide_box)
            load_image_thumbnail(original_image, reveal_box)

        if temp_png_created:
            os.remove(image_path)  # Delete the temporary PNG file

        upload_label.config(text="Finished")

    def load_image_thumbnail(image, label):
        try:
            img = image.copy()
            img.thumbnail((int(middle_frame.winfo_width() * 0.4), int(middle_frame.winfo_height() * 0.9)))  # Resize to fit in the hide/reveal box
            img = ImageTk.PhotoImage(img)
            label.config(image=img)
            label.image = img  # Keep a reference to the image to prevent garbage collection
        except Exception as e:
            print(f"Failed to load image: {e}")

    def clear_images():
        hide_box.config(image='', text='Hide')
        hide_box.image = None  # Remove reference to the image
        reveal_box.config(image='', text='Reveal')
        reveal_box.image = None  # Remove reference to the image
        upload_label.config(text="Drag and drop an image!")
        global processed_image
        global original_image
        global original_image_path
        global is_shuffled
        processed_image = None
        original_image = None
        original_image_path = None
        is_shuffled = False

    def save_image():
        if processed_image:
            base_name = os.path.basename(original_image_path)
            name, ext = os.path.splitext(base_name)
            suffix = "shuffled" if is_shuffled else "unshuffled"
            output_path = get_unique_filename(name, suffix, ".png")  # Save as PNG
            processed_image.save(output_path, "PNG")
            upload_label.config(text=f"Saved at {output_path}")

    def enlarge_image_handler(event):
        if event.widget.image:
            image = event.widget.image._PhotoImage__photo  # Extract the image object
            enlarge_image(image)

    # Create a vertical stack of 3 rows
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=3)
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)

    # Top row
    top_frame = ttk.Frame(root, padding="10 10 10 10", style="TFrame")  # Remove borderwidth and relief
    top_frame.grid(row=0, column=0, sticky="ew")
    top_frame.columnconfigure(0, weight=1)
    top_frame.columnconfigure(1, weight=4)
    top_frame.columnconfigure(2, weight=1)
    
    code_entry = ttk.Entry(top_frame, style="TEntry", foreground='gray', width=5, justify='center', font=("Helvetica", 24))
    code_entry.insert(0, 'Enter secret code')
    code_entry.bind('<FocusIn>', on_entry_click)
    code_entry.bind('<FocusOut>', on_focusout)
    code_entry.grid(row=0, column=1, sticky="ew", padx=(10, 10), ipady=10)
    
    # Second row (taller)
    middle_frame = ttk.Frame(root, padding="10 10 10 10", style="TFrame")  # Remove borderwidth and relief
    middle_frame.grid(row=1, column=0, sticky="nsew")
    middle_frame.columnconfigure(0, weight=1)
    middle_frame.columnconfigure(1, weight=1)

    hide_box = ttk.Label(middle_frame, text="Hide", relief="solid", anchor="center", borderwidth=2, style="TLabel")
    hide_box.place(relx=0.05, rely=0.05, relwidth=0.4, relheight=0.9)  # 90% of the row height and taking 40% of the width
    hide_box.drop_target_register(DND_FILES)
    hide_box.dnd_bind('<<Drop>>', lambda e: on_drop(e, hide_box))
    # hide_box.bind("<Button-1>", enlarge_image_handler)
    
    reveal_box = ttk.Label(middle_frame, text="Reveal", relief="solid", anchor="center", borderwidth=2, style="TLabel")
    reveal_box.place(relx=0.55, rely=0.05, relwidth=0.4, relheight=0.9)  # 90% of the row height and taking 40% of the width
    reveal_box.drop_target_register(DND_FILES)
    reveal_box.dnd_bind('<<Drop>>', lambda e: on_drop(e, reveal_box))
    # reveal_box.bind("<Button-1>", enlarge_image_handler)

    # Third row
    bottom_frame = ttk.Frame(root, padding="10 10 10 10", style="TFrame")  # Remove borderwidth and relief
    bottom_frame.grid(row=2, column=0, sticky="ew")
    bottom_frame.columnconfigure(0, weight=1)
    bottom_frame.columnconfigure(1, weight=1)
    bottom_frame.columnconfigure(2, weight=1)

    clear_button = ttk.Button(bottom_frame, text="Clear", command=clear_images, style="TButton.Clear.TButton")
    clear_button.grid(row=0, column=0, sticky="w")
    upload_label = ttk.Label(bottom_frame, text="Drag and drop an image!", anchor="center", style="TLabel")
    upload_label.grid(row=0, column=1, sticky="ew")
    save_button = ttk.Button(bottom_frame, text="Save", command=save_image, style="TButton.Save.TButton")
    save_button.grid(row=0, column=2, sticky="e")

    root.mainloop()

if __name__ == "__main__":
    main()
