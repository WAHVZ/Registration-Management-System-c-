"""
Registration Management System for Exhibitions
Author: Wali Ashraf
Usage: 
    python app/ Visitors.py
Notes:
    - Tested on Windows 10/ 11 with >= Pyhton 3.13
    - Requires pywin32 for printing, tk for GUI, reportlab for pdf printing and pillow for image/ canvas settings
"""


import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import datetime
import win32api, os, sqlite3, helper

DB_FILE = "Multan26L2.sqlite" # Name your db filename
TABLE_NAME = "registrants"    # Name your table name

visitor_count = 0
editing_last_entry_id = None

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS registrants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(30) NOT NULL,
            company VARCHAR(30),
            occupation VARCHAR(30),
            phone VARCHAR(30) NOT NULL,
            email VARCHAR(30),
            city VARCHAR(30),
            date_selected DATE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

is_submitting = False

def submit_form():
    global visitor_count, editing_last_entry_id, is_submitting

    if is_submitting:
        return  # prevent accidental double-submit
    is_submitting = True

    name = helper.clean_name(entry_name.get().strip())
    company = entry_company.get().strip() or "-"
    occupation = entry_occupation.get().strip() or "Visitor"
    occupation = ' '.join(word.capitalize() for word in occupation.split())    
    phone = entry_phone.get().strip()
    email = entry_email.get().strip()
    city = entry_city.get().strip() or "Multan"
    date_selected = datetime.now().strftime("%d-%m-%Y")

    if not name:
        messagebox.showwarning("Validation Error", "Name is required!")
        is_submitting = False
        return

    if (phone):
        if not (phone.isdigit() and phone.startswith("03") and len(phone) == 11):    # For pakistani phone numbers checking
            messagebox.showwarning("Validation Error", "Phone number must start with '03' and be 11 digits long.")
            is_submitting = False
            return

    try:
        conn = sqlite3.connect(DB_FILE, timeout=10)
        cursor = conn.cursor()

        if editing_last_entry_id is not None:
            # Update existing record (correction)
            cursor.execute(f"""
                UPDATE registrants 
                SET name=?, company=?, occupation=?, phone=?, email=?, city=?, date_selected=?
                WHERE id=?
            """, (name, company, occupation, phone, email, city, date_selected, editing_last_entry_id))
            editing_last_entry_id = None  # reset after successful update

        else:
            # Insert new record (normal new entry)
            cursor.execute(f"""
                INSERT INTO registrants (name, company, occupation, phone, email, city, date_selected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, company, occupation, phone, email, city, date_selected))
            visitor_count += 1  # increment only on new entry
            count_label.config(text=f"Visitors: {visitor_count}")
            print("Inserted new record")

        conn.commit()
        conn.close()

        # Badge generation
        data = {"name": name, "company": company, "occupation": occupation}
        #helper.generate_badge(data)
        badge_path = helper.generate_badge(data)
        helper.print_badge(badge_path)

        # Return focus to main window
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(lambda: root.attributes('-topmost', False))
        root.focus_force()

        clear_form()

    finally:
        is_submitting = False


def load_previous():
    global editing_last_entry_id

    conn = sqlite3.connect(DB_FILE)
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, company, occupation, phone, email, city FROM registrants ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()

    if result:
        editing_last_entry_id = result[0]  # store ID of the last record
        entry_name.delete(0, tk.END); entry_name.insert(0, result[1])
        entry_company.delete(0, tk.END); entry_company.insert(0, result[2])
        entry_occupation.delete(0, tk.END); entry_occupation.insert(0, result[3])
        entry_phone.delete(0, tk.END); entry_phone.insert(0, result[4])
        entry_email.delete(0, tk.END); entry_email.insert(0, result[5])
        entry_city.delete(0, tk.END); entry_city.insert(0, result[6])
    else:
        messagebox.showinfo("Info", "No previous entry found!")

def clear_form():
    global editing_last_entry_id
    for entry in [entry_name, entry_company, entry_occupation, entry_phone, entry_email, entry_city]:
        entry.delete(0, tk.END)

def handle_enter(event):
    if event.widget == submit_button:
        submit_form()

# Function to create gradient text image (horizontal gradient)
def create_gradient_text_image(text, font_path, font_size, width, height, color1, color2):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)

    # Horizontal gradient
    for x in range(width):
        ratio = x / width
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(x, 0), (x, height)], fill=(r, g, b))

    # Text mask
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    bbox = font.getbbox(text)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    mask_draw.text(((width - w) // 2, (height - h) // 2), text, font=font, fill=255)

    # Apply mask to gradient
    img.putalpha(mask)
    return ImageTk.PhotoImage(img)

# GUI Setup
root = tk.Tk()
root.title("Multan 2026 Registration Management System")
root.geometry("1000x650")
root.resizable(True, True)

# === Background Image ===
background_image = Image.open("C:/Users/Sukkur RMS User/Documents/TSS_Imp/Resources/bg.jpg")  # Put your background.png in the same folder or give complete path 
background_photo = ImageTk.PhotoImage(background_image.resize((1920, 1080)))
background_label = tk.Label(root, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# === Heading with Gradient Text === 
# Extract font from the zip file, download it and set its path here.
font_path = "C:/Users/Sukkur RMS User/Downloads/constantia/constan.ttf"  
gradient_image = create_gradient_text_image(
    text="The Solar Show\nMultan 2026",
    font_path=font_path,
    font_size=50,
    width=700,
    height=150,
    color1=(1, 255, 255),  # Color 1: #01FFFF (bright cyan)
    color2=(87, 160, 211)  # Color 2: #57A0D3 (soft blue)
)

heading_label = tk.Label(root, image=gradient_image, bg="black")
heading_label.image = gradient_image
heading_label.place(relx=0.425, rely=0.28, anchor="center")

# === Logo Image Top-Right Aligned with Heading ===
logo_image = Image.open("C:/Users/Sukkur RMS User/Documents/TSS_Imp/Resources/logo.png")  # Replace with your actual logo file name
logo_image = logo_image.resize((130, 130))  # Adjust size as needed
logo_photo = ImageTk.PhotoImage(logo_image)

logo_label = tk.Label(root, image=logo_photo, bg="black")
logo_label.image = logo_photo  # Keep reference
logo_label.place(relx=0.75, rely=0.307, anchor="center")  # Horizontally aligned with heading

# === Main Frame with styling ===
main_frame = tk.Frame(root, bg="#000000", bd=2, relief="ridge")
main_frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

bold_font = tkFont.Font(weight="bold", size=12)
entry_font = tkFont.Font(size=12)

# Grid layout
labels = ["Name*", "company", "Occupation", "Phone Number", "Email", "City"]
entries = []
entry_vars = []

for i, label in enumerate(labels):
    lbl = tk.Label(main_frame, text=label, font=bold_font, bg="#ffffff")
    lbl.grid(row=i//2, column=(i%2)*2, sticky="e", padx=(20, 10), pady=10)

    var = tk.StringVar()

    # Normal Entry field
    entry = tk.Entry(
        main_frame,
        textvariable=var,
        font=entry_font,
        width=30,
        bd=3,
        relief="groove"
        )

    entry.grid(row=i//2, column=(i%2)*2 + 1, padx=(0, 20), pady=10, sticky="ew")
    main_frame.grid_columnconfigure((i%2)*2 + 1, weight=1)

    entries.append(entry)
    entry_vars.append(var)

# Unpack in same order for backward compatibility
entry_name, entry_company, entry_occupation, entry_phone, entry_email, entry_city = entries

# Buttons
button_frame = tk.Frame(main_frame, bg="#ffffff")
button_frame.grid(row=3, column=0, columnspan=4, pady=30)

prev_button = tk.Button(button_frame, text="Previous", command=load_previous, width=15, font=bold_font, bg="#f0f0f0", relief="groove")
prev_button.grid(row=0, column=0, padx=10)

submit_button = tk.Button(button_frame, text="Submit", command=submit_form, width=15, font=bold_font, bg="#dfffdc", relief="groove")
submit_button.grid(row=0, column=1, padx=10)
submit_button.bind("<Return>", handle_enter)

# Initial DB setup
setup_database()

# === Visitor Count Label (Bottom Right) ===
count_label = tk.Label(root, text="Visitors: 0", font=("Constantia", 16, "bold"), fg="white", bg="black")
count_label.place(relx=0.78, rely=0.93, anchor="se")

root.mainloop()
