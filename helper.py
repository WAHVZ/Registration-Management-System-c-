import re
import os
from reportlab.lib.pagesizes import portrait
from reportlab.pdfgen import canvas
import win32api


def clean_name(name: str):
    """
    Cleans and standardizes visitor names according to local conventions.
    Returns cleaned name string.
    """
    original_name = name.strip()
    name = original_name

    # 1️⃣ Remove unwanted characters and normalize spaces
    name = re.sub(r'[^A-Za-z\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    # 2️⃣ Standardize casing (lowercase temporarily for matching)
    name = name.lower()

    # 3️⃣ Common Arabic/Urdu-origin prefix spacing fixes
    name = re.sub(r'\babdul\s*([a-z])', r'abdul \1', name)
    name = re.sub(r'\babdal\s*([a-z])', r'abdul \1', name)
    name = re.sub(r'\bmuhammad\s*([a-z])', r'muhammad \1', name)
    name = re.sub(r'\bmohammad\s*([a-z])', r'mohammad \1', name)
    name = re.sub(r'\bsyed\s*([a-z])', r'syed \1', name)
    name = re.sub(r'\bsheikh\s*([a-z])', r'sheikh \1', name)
    name = re.sub(r'\bmian\s*([a-z])', r'mian \1', name)
    name = re.sub(r'\bchaudhry\s*([a-z])', r'chaudhry \1', name)
    name = re.sub(r'\bghulam\s*([a-z])', r'ghulam \1', name)
    name = re.sub(r'\bgul\s*([a-z])', r'gul \1', name)

    # 4️⃣ Convert Abd Al / Abdal to Abdul
    name = re.sub(r'\babd\s+al\s+', 'abdul ', name)
    name = re.sub(r'\babdal\b', 'abdul ', name)

    # 5️⃣ Common suffix-based spacing fixes (Pakistani-style last names)
    suffixes = [
        "ahmed", "ahmad", "khan", "raza", "malik", "hasan", "hassan",
        "hussain", "farooq", "arif", "iqbal", "rafiq", "bashir", "aslam",
        "imran", "nasir", "amir", "akbar", "ashraf", "siddique",
        "shah", "bibi", "pasha", "ather"
    ]
    for suf in suffixes:
        name = re.sub(rf'([a-z]){suf}\b', rf'\1 {suf}', name)

    # 6️⃣ Remove hyphens and fix “Aa…” issues
    name = re.sub(r'-', ' ', name)
    name = re.sub(r'\baa+([a-z]+)', r'a\1', name)

    # 7️⃣ Collapse spaces again
    name = re.sub(r'\s+', ' ', name).strip()

    # 8️⃣ Title case properly
    name = ' '.join(word.capitalize() for word in name.split())

    return name


def print_badge(file_path):
    """Prints a badge PDF file using the system's default printer."""
    if not file_path:
        print("⚠️ No file path provided to print_badge().")
        return
    if os.path.exists(file_path):
        try:
            win32api.ShellExecute(0, "print", file_path, None, ".", 0)
        except Exception as e:
            print(f"⚠️ Printing failed: {e}")
    else:
        print(f"⚠️ File does not exist: {file_path}")


def truncate_to_last_word(text, max_length):
    """Cuts a string at word boundary if it exceeds max_length."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    return truncated[:last_space] if last_space != -1 else truncated


def generate_badge(data):
    """
    Generates a badge PDF and returns its full file path.
    Expected data dict keys: name, company, occupation
    """
    folder = os.path.join(os.path.dirname(__file__), "Badges")
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"{data['name']}_badge.pdf")

    # Clean and truncate
    name = truncate_to_last_word(data['name'], 18)
    company = truncate_to_last_word(data['company'], 20)
    occupation = truncate_to_last_word(data['occupation'], 20)

    # Create PDF badge
    c = canvas.Canvas(file_path, pagesize=portrait((4 * 72, 5.5 * 72)))  # 4x5.5 inches
    c.setFont("Times-Bold", 25)
    c.drawString(65, 220, name)
    c.setFont("Times-Roman", 23)
    c.drawString(65, 160, company)
    c.setFont("Times-Roman", 22)
    c.drawString(65, 105, occupation)
    c.save()

    return file_path
