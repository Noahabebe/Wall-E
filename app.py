from flask import Flask, render_template, request, send_file
import qrcode
import os
from passlib.pwd import genword
from passlib.pkcs12 import create_pkcs12
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Temporary directory to store generated pass files
PASS_DIR = 'passes'

# Create the temporary directory if it doesn't exist
os.makedirs(PASS_DIR, exist_ok=True)

# Route for the main page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Route for generating the pass
@app.route('/generate', methods=['POST'])
def generate_pass():
    if request.method == 'POST':
        # Get user input (contact info and customizable metadata)
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        pass_type_identifier = request.form.get('passTypeIdentifier')
        organization_name = request.form.get('organizationName')
        description = request.form.get('description')

        # Generate QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(f'Name: {name}\nPhone: {phone}\nEmail: {email}\nPass Type Identifier: {pass_type_identifier}\nOrganization Name: {organization_name}\nDescription: {description}')
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')

        # Create a pass
        pass_filename = f'{genword(entropy=32)}.pkpass'
        pass_path = os.path.join(PASS_DIR, pass_filename)

        # Generate card image with QR code
        card_image = generate_card_image(name, email, phone, qr_img)

        # Save the card image
        card_image.save(os.path.join(PASS_DIR, 'card.png'))

        # Create the pass
        create_pass(name, email, phone, pass_type_identifier, organization_name, description, pass_path)

        return send_file(pass_path, mimetype='application/vnd.apple.pkpass', as_attachment=True, attachment_filename='wallet_pass.pkpass')

# Function to generate card image with QR code
def generate_card_image(name, email, phone, qr_code):
    # Open a card template image
    card_template = Image.open('card_template.png')

    # Paste QR code onto the card template
    card_template.paste(qr_code, (50, 50))

    # Add text to the card
    draw = ImageDraw.Draw(card_template)
    font = ImageFont.truetype('arial.ttf', size=30)
    draw.text((100, 300), f"Name: {name}", fill='black', font=font)
    draw.text((100, 350), f"Email: {email}", fill='black', font=font)
    draw.text((100, 400), f"Phone: {phone}", fill='black', font=font)

    return card_template

# Function to create the pass
def create_pass(name, email, phone, pass_type_identifier, organization_name, description, pass_path):
    pass_metadata = {
        'passTypeIdentifier': pass_type_identifier,
        'teamIdentifier': 'YOUR_TEAM_IDENTIFIER',
        'organizationName': organization_name,
        'description': description,
        'serialNumber': '123456',
        'backgroundColor': 'rgb(255, 255, 255)',
        'foregroundColor': 'rgb(0, 0, 0)',
        'labelColor': 'rgb(0, 0, 0)',
        'logoText': 'Your Logo',
        'authenticationToken': 'YOUR_AUTHENTICATION_TOKEN',
        'webServiceURL': 'https://example.com/passes/',
        'barcode': {
            'format': 'PKBarcodeFormatQR',
            'message': f"Name: {name}\nPhone: {phone}\nEmail: {email}",
            'messageEncoding': 'UTF-8'
        }
    }

    # Create the pass
    create_pkcs12(pass_path, 'your_certificate.pem', 'your_private_key.pem', 'your_password', 'card.png', pass_metadata)

if __name__ == '__main__':
    app.run(debug=True)

