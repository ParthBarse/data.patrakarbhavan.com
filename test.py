import json
from fpdf import FPDF
from num2words import num2words

# 1. Your original in‐memory dict
data = {
    "count": 1,
    "entity": "collection",
    "items": [
        {
            "acquirer_data": {"rrn": "512057608660"},
            "amount": 107500,
            "amount_captured": None,
            "amount_refunded": 0,
            "bank": None,
            "captured": True,
            "card_id": None,
            "contact": "+919970239999",
            "created_at": 1745989355,
            "currency": "INR",
            "description": "Booking for PUWJ | B. V. Rao Press Conference Hall",
            "email": "mnvs.prashantkanojia@gmail.com",
            "entity": "payment",
            "error_code": None,
            "error_description": None,
            "error_reason": None,
            "error_source": None,
            "error_step": None,
            "fee": 2538,
            "id": "pay_QP98wvgebSocxd",
            "international": False,
            "invoice_id": None,
            "method": "upi",
            "notes": [
                {
                    "address": "फ्लॅट 1 श्रीपाद आप्ट.उजवी भुसारी कॉलनी कोथरुड",
                    "baseAmount": "890",
                    "date": "2025-05-02",
                    "duration": "30",
                    "email": ["mnvs.prashantkanojia@gmail.com"],
                    "end_time": "15:30",
                    "govId": "YES ",
                    "gst": 160,
                    "gstNo": "",
                    "insName": "मनसे ",
                    "name": ["महाराष्ट्र नवनिर्माण विद्यार्थी सेना "],
                    "phnNo": ["9970239999"],
                    "pinCode": "411038",
                    "platformFee": 25,
                    "serviceId": ["press-conference"],
                    "serviceName": ["PUWJ | B. V. Rao Press Conference Hall"],
                    "start_time": "15:00",
                    "subCatType": "Press Conference",
                    "subject": "बोलक्या रेषा व्यंगचित्रे प्रदर्शन व कार्यशाळा "
                }
            ],
            "order_id": "order_QP98dET57DrbGx",
            "provider": None,
            "refund_status": None,
            "reward": None,
            "status": "captured",
            "tax": 388,
            "upi": {"payer_account_type": "bank_account", "vpa": "mnvs.prashantkanojia-2@okaxis"},
            "vpa": "mnvs.prashantkanojia-2@okaxis",
            "wallet": None
        }
    ]
}

new_data = {
    "acquirer_data": {"rrn": "512057608660"},
    "amount": 107500,
    "amount_captured": None,
    "amount_refunded": 0,
    "bank": None,
    "captured": True,
    "card_id": None,
    "contact": "+919970239999",
    "created_at": 1745989355,
    "currency": "INR",
    "description": "Booking for PUWJ | B. V. Rao Press Conference Hall",
    "email": "mnvs.prashantkanojia@gmail.com",
    "entity": "payment",
    "error_code": None,
    "error_description": None,
    "error_reason": None,
    "error_source": None,
    "error_step": None,
    "fee": 2538,
    "id": "pay_QP98wvgebSocxd",
    "international": False,
    "invoice_id": None,
    "method": "upi",
    "address": "फ्लॅट 1 श्रीपाद आप्ट.उजवी भुसारी कॉलनी कोथरुड",
    "baseAmount": "890",
    "date": "2025-05-02",
    "duration": "30",
    "email": ["mnvs.prashantkanojia@gmail.com"],
    "end_time": "15:30",
    "govId": "YES ",
    "gst": 160,
    "gstNo": "",
    "insName": "मनसे ",
    "name": ["महाराष्ट्र नवनिर्माण विद्यार्थी सेना "],
    "phnNo": ["9970239999"],
    "pinCode": "411038",
    "platformFee": 25,
    "serviceId": ["press-conference"],
    "serviceName": ["PUWJ | B. V. Rao Press Conference Hall"],
    "start_time": "15:00",
    "subCatType": "Press Conference",
    "subject": "बोलक्या रेषा व्यंगचित्रे प्रदर्शन व कार्यशाळा ",
            "order_id": "order_QP98dET57DrbGx",
            "provider": None,
            "refund_status": None,
            "reward": None,
            "status": "captured",
            "tax": 388,
            "upi": {"payer_account_type": "bank_account", "vpa": "mnvs.prashantkanojia-2@okaxis"},
            "vpa": "mnvs.prashantkanojia-2@okaxis",
            "wallet": None,
            "invoice_no": "OR-1005"
}
# 2. Serialize to a JSON string with Unicode intact
json_str = json.dumps(data, ensure_ascii=False)

# 3. (In‐memory) parse it back into a Python dict
#    This dict will be byte‐safe and preserve all Marathi characters.
safe_dict = json.loads(json_str)

# Now `safe_dict` is your fully‐formed dict, ready to return or manipulate:
print(safe_dict)


class PDF(FPDF):
    def header(self):
        """ Set background image """
        self.image("template2.jpeg", x=0, y=0, w=210, h=297)  # A4 size
        self.add_font("notor", "", "notor.ttf")
        self.set_font("notor", size=12)


def generate_invoice(receipt_data):
    """ Generates and saves an invoice as a PDF and returns the invoice link & file path """
    pdf = PDF()
    pdf.add_page()
    pdf.add_font("notor", "", "notor.ttf")
    # pdf.set_font("notor", size=12)
    pdf.set_font("notor", size=10)

    # Convert values
    receipt_data["words"] = num2words(
        receipt_data["amount"]/100, lang='en_IN').capitalize()
    receipt_data["tcswords"] = num2words(
        receipt_data["gst"], lang='en_IN').capitalize()
    receipt_data['base'] = float(receipt_data['baseAmount'])

    # Invoice details
    pdf.set_xy(101, 27)
    pdf.cell(0, 10, f"{receipt_data['invoice_no']}", ln=True)
    from datetime import datetime

    # Get current date in desired format (e.g., 04-04-2025)
    current_date = datetime.now().strftime("%d-%m-%Y")

    pdf.set_xy(141, 27)
    pdf.cell(0, 10, f"{current_date}", ln=True)

    # Customer details
    pdf.set_xy(14, 60)
    pdf.add_font("notob", "", "notob.ttf")
    pdf.set_font("notob", size=10)
    pdf.cell(0, 10, f"Name: {receipt_data['name']}", ln=True)

    pdf.set_xy(101, 93)
    pdf.set_font("notor", size=10)
    pdf.cell(
        0, 10, f"Booking Date: {receipt_data['date']}, Time: {receipt_data['start_time']} - {receipt_data['end_time']}", ln=True)

    pdf.set_xy(14, 80)
    pdf.cell(0, 10, f"Phone: {receipt_data['phnNo']}", ln=True)

    pdf.set_xy(14, 69)
    pdf.multi_cell(
        80, 4, f"Address:{receipt_data['address']}, Pincode-{receipt_data['pinCode']}")

    pdf.set_xy(14, 90)
    pdf.cell(0, 10, f"Email: {receipt_data['email']}", ln=True)

    # Amount details
    pdf.set_xy(170, 163)
    pdf.add_font("notob", "", "notob.ttf")
    pdf.set_font("notob", size=10)
    pdf.cell(0, 10, f"{receipt_data['amount']/100}", ln=True)

    pdf.set_xy(14, 172)
    pdf.add_font("notob", "", "notob.ttf")
    pdf.set_font("notob", size=10)
    pdf.cell(0, 10, f"{receipt_data['words']}", ln=True)

    # Tax & GST breakdown
    pdf.set_xy(60, 190)
    pdf.set_font("notor", size=10)
    pdf.cell(0, 10, f"{receipt_data['base']}", ln=True)
    pdf.set_xy(90, 190)
    pdf.cell(0, 10, f"9", ln=True)
    pdf.set_xy(105, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(125, 190)
    pdf.cell(0, 10, f"9", ln=True)
    pdf.set_xy(140, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(175, 190)
    pdf.cell(0, 10, f"{receipt_data['gst']}", ln=True)

    pdf.set_xy(60, 200)
    pdf.cell(0, 10, f"{receipt_data['base']}", ln=True)
    pdf.set_xy(105, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(140, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
    pdf.set_xy(175, 200)
    pdf.cell(0, 10, f"{receipt_data['gst']}", ln=True)

    pdf.set_xy(14, 213)
    pdf.cell(0, 10, f"{receipt_data['tcswords']}", ln=True)

    # Conditional formatting based on subCatType
    if receipt_data['subCatType'] == 'Program':
        pdf.set_xy(30, 144)
        pdf.cell(0, 10, f"Platform Fee", ln=True)
        pdf.set_xy(70, 136)
        pdf.cell(0, 10, f"Output CGST@9%", ln=True)
        pdf.set_xy(136, 120)
        pdf.cell(0, 10, f"18", ln=True)
        pdf.set_xy(148, 128)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(148, 136)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(70, 128)
        pdf.cell(0, 10, f"Output SGST@9%", ln=True)
        pdf.set_xy(30, 120)
        pdf.cell(0, 10, f"{receipt_data['serviceName']}", ln=True)
        pdf.set_xy(170, 120)
        pdf.cell(0, 10, f"{receipt_data['baseAmount']}", ln=True)
        pdf.set_xy(170, 136)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 128)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 144)
        pdf.cell(0, 10, f"{receipt_data['platformFee']}", ln=True)
    else:
        pdf.set_xy(30, 152)
        pdf.cell(0, 10, f"Platform Fee", ln=True)
        pdf.set_xy(70, 144)
        pdf.cell(0, 10, f"Output CGST@9%", ln=True)
        pdf.set_xy(136, 120)
        pdf.cell(0, 10, f"18", ln=True)
        pdf.set_xy(148, 136)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(148, 144)
        pdf.cell(0, 10, f"9%", ln=True)
        pdf.set_xy(70, 136)
        pdf.cell(0, 10, f"Output SGST@9%", ln=True)
        pdf.set_xy(30, 120)
        pdf.cell(0, 10, f"{receipt_data['serviceName']}", ln=True)
        pdf.set_xy(30, 128)
        pdf.cell(0, 10, f"News Distribution", ln=True)
        pdf.set_xy(136, 128)
        pdf.cell(0, 10, f"18", ln=True)
        pdf.set_xy(170, 120)
        pdf.cell(
            0, 10, f"{float(receipt_data['baseAmount']) - 254.24}", ln=True)
        pdf.set_xy(170, 144)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 136)
        pdf.cell(0, 10, f"{receipt_data['gst']/2}", ln=True)
        pdf.set_xy(170, 152)
        pdf.cell(0, 10, f"{receipt_data['platformFee']}", ln=True)
        pdf.set_xy(170, 128)
        pdf.cell(0, 10, f"254.24", ln=True)

    # Save PDF
    # Generate PDF in memory
    current_date = datetime.now().strftime('%Y-%m-%d')
    pdf_filename = f"invoice_{receipt_data['invoice_no']}.pdf"
    pdf_path = f"{pdf_filename}"  # Temporary storage for uploading
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as pdf_file:
        files = {"file": (pdf_filename, pdf_file, "application/pdf")}

    # Upload PDF to external server
    # with open(pdf_path, "rb") as pdf_file:
    #     files = {"file": (pdf_filename, pdf_file, "application/pdf")}
    #     response = requests.post(
    #         "https://api2.patrakarbhavan.com/upload", files=files)

    # invoice_link = ""

    # # Check if the upload was successful
    # if response.status_code == 200:
    #     # Assuming the API returns the file URL
    #     invoice_link = response.json().get("file_url")
    # else:
    #     print("Error uploading file")

    # # invoice_link = f"https://files.patrakarbhavan.com/receipts/{current_date}/invoice_{receipt_data['invoice_no']}.pdf"
    # pdf_file_path = invoice_link.replace(
    #     "https://files.patrakarbhavan.com", "/home/rzeaiuym/files.patrakarbhavan.com")
    return pdf_path


generate_invoice(new_data)
