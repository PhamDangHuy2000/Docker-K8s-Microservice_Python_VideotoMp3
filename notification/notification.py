import os
import json
import smtplib

from email.message import EmailMessage

def send_notification(message):
    try:
        message = json.loads(message)
        mp3_file_id = message.get("mp3_file_id")
        # tài khoản người gửi phải cho phép truy cập vào các ứng dụng không phải của Google
        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_PASSWORD")
        receiver_address = message.get("username")

        email_content = f"MP3 file_id: {mp3_file_id} is now READY!"

        # Google không còn hỗ trợ các ứng dụng kém an toàn hơn

        email_msg = EmailMessage()
        email_msg.set_content(email_content)
        email_msg["Subject"] = "MP3 Download"
        email_msg["From"] = sender_address
        email_msg["To"] = receiver_address

        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(email_msg)
        session.quit()

        print(f"Mail sent with content: {email_content}")

    except Exception as e:
        print(e)
        return e
