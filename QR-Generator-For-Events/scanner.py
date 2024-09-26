from flask import Flask, render_template, request
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image
import qrcode
import io
import csv
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get the QR code data as a string
            qr_data_str = request.form['qr_code_data']

            # Generate QR code image from the string data
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data_str)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Decode the QR code using pyzbar
            decoded_objs = decode(Image.open(io.BytesIO(img_byte_arr)), symbols=[ZBarSymbol.QRCODE])

            # Check if any QR codes were detected
            if not decoded_objs:
                return "No QR code detected in the image. Please try scanning again."

            # Extract the decoded data
            decoded_data = decoded_objs[0].data.decode('utf-8')

            # Extract information
            lines = decoded_data.splitlines()

            # Check if the QR code has the expected format
            if len(lines) != 7 or lines[0].strip() != "FROSH NIGHT 2024":
                return "Invalid QR code format."

            qr_id = lines[1].strip().split(': ')[1]
            qr_attendee_name = lines[2].strip().split(': ')[1]
            qr_id_number = lines[3].strip().split(': ')[1]
            qr_email_address = lines[4].strip().split(': ')[1]
            qr_school = lines[5].strip().split(': ')[1]
            qr_block = lines[6].strip().split(': ')[1]

            # Get the current time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Read the registration CSV file
            with open('FroshNight2024Registration.csv', 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)  # Read all rows into a list

            # Find a matching row in the registration data
            matching_row = None
            for row in rows:
                if (
                    row['id'] == qr_id and
                    row['attendee_name'] == qr_attendee_name and
                    row['id_number'] == qr_id_number and
                    row['email_address'] == qr_email_address and
                    row['school'] == qr_school and
                    row['block'] == qr_block
                ):
                    matching_row = row
                    break

            if matching_row:
                if matching_row['status'] == 'Confirmed':
                    return "NO CHANGES MADE! Registration already confirmed."
                else:
                    # Update the status and time in the matching row
                    matching_row['status'] = 'Confirmed'
                    matching_row['time'] = current_time

                    # Write the updated data back to the registration CSV file
                    with open('FroshNight2024Registration.csv', 'w', newline='') as csvfile:
                        fieldnames = ['id', 'attendee_name', 'id_number', 'email_address', 'school', 'block', 'status', 'time']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)

                    # Append the confirmed data to FroshNight2024Confirmed.csv
                    file_exists = os.path.isfile('FroshNight2024Confirmed.csv')
                    with open('FroshNight2024Confirmed.csv', 'a', newline='') as confirmed_csvfile:
                        fieldnames = ['id', 'attendee_name', 'id_number', 'email_address', 'school', 'block', 'status', 'time']
                        writer = csv.DictWriter(confirmed_csvfile, fieldnames=fieldnames)

                        # Write the header only if the file is new
                        if not file_exists:
                            writer.writeheader()

                        writer.writerow(matching_row)

                    return "QR CODE SCANNED SUCCESSFULLY! Registration confirmed."
            else:
                return "No matching registration found for this QR code."

        except Exception as e:
            return f"Error processing QR code: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)