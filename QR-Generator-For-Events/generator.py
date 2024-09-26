import csv
import qrcode

def generate_qr_codes_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )


            data = f"FROSH NIGHT 2024\n" \
                   f"id: {row['id']}\n" \
                   f"attendee_name: {row['attendee_name']}\n" \
                   f"id_number: {row['id_number']}\n" \
                   f"email_address: {row['email_address']}\n" \
                   f"school: {row['school']}\n" \
                   f"block: {row['block']}"

            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img.save(f"{row['id']}_{row['attendee_name']}.png")

csv_file_path = 'FroshNight2024Registration.csv'
generate_qr_codes_from_csv(csv_file_path)