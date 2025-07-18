import pytesseract, re, datetime
from PIL import Image
from utils.expenseTracker import ExpenseManager

exp_mgr = ExpenseManager()

def scan_bill(image_bytes, user_email: str):
    img = Image.open(image_bytes).convert("RGB")
    text = pytesseract.image_to_string(img)

    # Regex patterns (adjust for your receipts)
    amount_re = re.search(r'(?:total|amount|rs\.?)\s*[:₹$]?\s*(\d+(?:\.\d{2})?)', text, re.I)
    date_re   = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
    vendor_re = re.search(r'(.+?)\s*(?:restaurant|store|mart|shop|pvt|ltd)', text, re.I)

    amount = float(amount_re.group(1)) if amount_re else 0.0
    date_str = date_re.group(1) if date_re else datetime.date.today().isoformat()
    vendor = vendor_re.group(1).strip() if vendor_re else "Unknown"

    exp_mgr.add_expense(user_email, vendor, amount, date_str)
    return vendor, amount, date_str