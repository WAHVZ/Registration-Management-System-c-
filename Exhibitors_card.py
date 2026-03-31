import gspread
import time, os
from reportlab.lib.pagesizes import portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import win32api

# Function to truncate text at last space before max length
def truncate_to_last_word(text, max_length):
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    return truncated[:last_space] if last_space != -1 else truncated

# Function to retrieve new entries since last checked row
def get_new_entries(worksheet, last_checked_row, end):
    all_entries = worksheet.get_all_values()
    return all_entries[last_checked_row:end]

# Function to generate badge
def generate_badge(data):
    folder = "C:/Users/Sukkur RMS User/Desktop/Peshawar_26/Exhibitors"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, f"{data['name']}_badge.pdf")
    
    # Truncate fields
    name = truncate_to_last_word(data['name'], 18)
    designation = truncate_to_last_word(data['designation'], 20)
    company = truncate_to_last_word(data['company'], 20)

    # Create compact badge (4x5.5 inches)
    c = canvas.Canvas(file_path, pagesize=portrait((4 * 72, 5.5 * 72)))
    c.setFont("Times-Bold", 23)
    c.drawString(45, 230, company)        # Company position
    c.setFont("Times-Roman", 25)
    c.drawString(45, 165, name)            # name position
    c.setFont("Times-Roman", 24)
    c.drawString(45, 110, designation)     # Designation position
    c.save()
    
    return file_path

# Function to print badge
def print_badge(file_path):
    if os.path.exists(file_path):
        win32api.ShellExecute(0, "print", file_path, None, ".", 0)

# Process new entries
def process_new_entries(new_entries):
    for entry in new_entries:
        if len(entry) >= 3:  # Ensure entry has all required fields
            data = {
                'name': entry[0],        # First column - Name
                'designation': entry[1], # Second column - Designation
                'company': entry[2]      # Third column - Company
            }
            # generate_badge(data)
            badge_path = generate_badge(data)
            print_badge(badge_path)

# Main execution
if __name__ == "__main__":
    # Authenticate with Google Sheets
    gc = gspread.service_account("C:/Users/Sukkur RMS User/Documents/TSS_Imp/my_key.json")
    sh = gc.open("Prints Check")
    worksheet = sh.sheet1
    
    last_checked_row = 1 # Start from row 1 (header would be row 0 if exists)
    end = 2
   
    new_entries = get_new_entries(worksheet, last_checked_row, end)
    if new_entries:
        process_new_entries(new_entries)
        last_checked_row += len(new_entries)
