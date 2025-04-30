import json

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

# 2. Serialize to a JSON string with Unicode intact
json_str = json.dumps(data, ensure_ascii=False)

# 3. (In‐memory) parse it back into a Python dict
#    This dict will be byte‐safe and preserve all Marathi characters.
safe_dict = json.loads(json_str)

# Now `safe_dict` is your fully‐formed dict, ready to return or manipulate:
print(safe_dict)
