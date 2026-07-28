import smtplib
from pathlib import Path
import os

from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes


env_file = Path(__file__).resolve().parent / 'connect.env'
load_dotenv(env_file)


def send_email(subject, message, recipient, file_paths):
    sender = os.getenv('EMAIL')
    password = os.getenv('GMAIL_KEY')

    if not password:
        print("Еhe password was not found!!!")
        return
    
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender 
    msg["To"] = recipient
    msg.attach(MIMEText(message, 'plain', 'utf-8'))

    if file_paths:
        for file_path in file_paths:
            file_path = file_path.strip().strip("'\"")
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)

                ctype, encoding = mimetypes.guess_type(file_path)
                if ctype is None or encoding is not None:
                    maintype, subtype = "application", "octet-stream"
                else:
                    maintype, subtype = ctype.split("/", 1)

                with open(file_path, "rb") as attachment:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}",
                )
                msg.attach(part)
                print(f"The file is attached: {filename}")
            else:
                print(f"The file was not found and skipped: {file_path}")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())  
        print("Your message has been sent successfully!!")

    except Exception as _e:
        print(f"{_e}\nCheck your email or password!")



def main():
    recipient = input("Input recipient: ")
    subject = input("Input your subject: ")
    msg = input("Input your message: ")
    files_input = input("Specify the file paths separated by commas (for example, doc1.pdf, photo.jpg): ")
    files_list = [f for f in files_input.split(",") if f.strip()]

    send_email(subject, msg, recipient, files_list)

if __name__ == "__main__":
    main()