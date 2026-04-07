"""
utils/qr_generator.py - QR Code Generator
AICTE Activity & Points Management System

Generates QR codes for event attendance tracking.
"""

import os
import qrcode
from config import QR_CODE_DIR


def generate_event_qr(event_id, qr_token, base_url='http://localhost:5000'):
    """
    Generate a QR code for an event's attendance URL.

    Args:
        event_id: The event's database ID
        qr_token: Unique token for this event's QR code
        base_url: The application's base URL

    Returns:
        str: Path to the generated QR code image (relative to static/)
    """
    # Build the attendance URL that the QR code will encode
    attendance_url = f"{base_url}/student/attend/{qr_token}"

    # Create QR code instance with settings for good readability
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(attendance_url)
    qr.make(fit=True)

    # Create the QR code image with custom colors
    img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff")

    # Save the image
    filename = f"event_{event_id}_{qr_token}.png"
    filepath = os.path.join(QR_CODE_DIR, filename)
    img.save(filepath)

    # Return relative path for use in templates
    return f"qrcodes/{filename}"


def get_qr_path(event_id, qr_token):
    """
    Get the path to an existing QR code image.
    Returns the path if it exists, None otherwise.
    """
    filename = f"event_{event_id}_{qr_token}.png"
    filepath = os.path.join(QR_CODE_DIR, filename)
    if os.path.exists(filepath):
        return f"qrcodes/{filename}"
    return None
