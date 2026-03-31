# Function to truncate text at last space before max length
import os, reportlab
from reportlab.lib.pagesizes import portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import win32api

def truncate_to_last_word(text, max_length):
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    return truncated[:last_space] if last_space != -1 else truncated

# Function to generate badge
def generate_badge(data):
    folder = "C:/Users/Sukkur RMS User/Desktop/Peshawar_26/Exhibitors"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, f"{data['name']}_badge.pdf")
    
    # Truncate fields
    name = truncate_to_last_word(data['name'], 20)
    designation = truncate_to_last_word(data['designation'], 20)
    company = truncate_to_last_word(data['company'], 20)

    # Create compact badge (4x5.5 inches)
    c = canvas.Canvas(file_path, pagesize=portrait((4 * 72, 5.5 * 72)))
    c.setFont("Times-Bold", 23)
    c.drawString(45, 245, company)        # Company position
    c.setFont("Times-Roman", 25)
    c.drawString(45, 180, name) # name position     
    c.setFont("Times-Roman", 24)
    c.drawString(45, 125, designation)     # Designation position
    c.save()
    
    return file_path

# Function to print badge
def print_badge(file_path):
    if os.path.exists(file_path):
        win32api.ShellExecute(0, "print", file_path, None, ".", 0)
        
Ename = str(input("Enter Name: "))
Edesignation = str(input("Enter Designation: "))
Ecompany = str(input("Enter Company: "))

data = {
                'name': Ename,        # First column - Name
                'designation': Edesignation, # Second column - Designation
                'company': Ecompany     # Third column - Company
            }
# generate_badge(data)
badge_path = generate_badge(data)
print_badge(badge_path)