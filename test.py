import smtplib
from pathlib import Path
import os

from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import mimetypes
import customtkinter as ctk
from tkinter import messagebox, filedialog



env_file = Path(__file__).resolve().parent / 'connect.env'
load_dotenv(env_file)

class AttachmentManager(ctk.CTkFrame):
    def __init__(self, master, width=560, height=150, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)

        self.pack_propagate(False)
        
        self.selected_files = []

        self.add_btn = ctk.CTkButton(self, text="📁 Browse...", width=100, command=self.open_file_dialog)
        self.add_btn.pack(anchor="w", padx=5, pady=5)

        self.files_container = ctk.CTkScrollableFrame(self, width=540, height=40)
        self.files_container.pack(padx=5, pady=(0, 5), fill="both", expand=True)
        
        self._render_file_list()

    def open_file_dialog(self):
        files = filedialog.askopenfilenames(title="Choose files")
        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
            self._render_file_list()

    def remove_file(self, path):
        if path in self.selected_files:
            self.selected_files.remove(path)
        self._render_file_list()

    def _render_file_list(self):
        for child in self.files_container.winfo_children():
            child.destroy()

        if not self.selected_files:
            empty_lbl = ctk.CTkLabel(self.files_container, text="No files attached", text_color="gray")
            empty_lbl.pack(pady=2)
            return

        for path in self.selected_files:
            row = ctk.CTkFrame(self.files_container, fg_color="transparent")
            row.pack(fill="x", pady=1, padx=2)

            filename = os.path.basename(path)
            name_lbl = ctk.CTkLabel(row, text=filename, anchor="w")
            name_lbl.pack(side="left", fill="x", expand=True)

            del_btn = ctk.CTkButton(row, text="❌", width=25, height=20, fg_color="transparent", hover_color="#550000", text_color="red", command=lambda p=path: self.remove_file(p))
            del_btn.pack(side="right", padx=2)

    def get_files(self):
        return self.selected_files

    def clear_files(self):
        self.selected_files.clear()
        self._render_file_list()

    
def send_email(subject:str, message:str, recipient:str, file_paths:list):
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
            clean_path = Path(str(file_path).strip().strip("'\""))
            if clean_path.exists():
                filename = clean_path.name

                ctype, encoding = mimetypes.guess_type(clean_path)
                if ctype is None or encoding is not None:
                    maintype, subtype = "application", "octet-stream"
                else:
                    maintype, subtype = ctype.split("/", 1)

                with open(clean_path, "rb") as attachment:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{filename}"',
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
        server.quit()
        messagebox.showinfo("Wearing!", "Your message has been sent successfully!!")
        return True

    except Exception as _e:
        messagebox.showerror('Error!', f"{_e}\nCheck your email or password!")
        return False



def main():
    def handle_send():
        success = send_email(subject=subject.get(), message=msg.get("1.0", "end-1c"), recipient=recipient.get(), file_paths=attachment_manager.get_files())

        if success:
            recipient.delete(0, 'end')
            subject.delete(0, 'end')
            msg.delete("1.0", 'end')
            attachment_manager.clear_files()


    w:int = 900
    h:int  = 900

    win = ctk.CTk()
    win.geometry(f'{w}x{h}')

    #       BODY
    email_frame = ctk.CTkFrame(master=win)
    email_frame.pack(pady=20)
    
    #       RECIPIENT
    recipient_frame = ctk.CTkFrame(master=email_frame)
    recipient_label = ctk.CTkLabel(recipient_frame, text='To:', font=("Times New Roman", 18))
    recipient_label.pack(side='left',padx=10, pady=5)
    recipient = ctk.CTkEntry(recipient_frame, width=560, placeholder_text='')
    recipient.pack(side='left', padx=10, pady=5)
    recipient_frame.pack(padx=20, pady=10, anchor='w')

    #       SUBJECT
    subject_frame = ctk.CTkFrame(master=email_frame)
    subject_label = ctk.CTkLabel(subject_frame, text='Theme:', font=("Times New Roman", 18))
    subject_label.pack(side='left',padx=10, pady=5)
    subject = ctk.CTkEntry(subject_frame, width=530, placeholder_text='')
    subject.pack(side='left', padx=10, pady=5)
    subject_frame.pack(padx=20, pady=10, anchor='w')


    #       MESSAGE
    msg_frame = ctk.CTkFrame(master=email_frame)
    
    attachments_label = ctk.CTkLabel(msg_frame, text='Files:', font=("Times New Roman", 18))
    attachments_label.pack(padx=30, pady=(10, 0), anchor='w')
    attachment_manager = AttachmentManager(master=msg_frame)
    attachment_manager.pack(padx=10, pady=5, fill="x")

    msg_label = ctk.CTkLabel(msg_frame, text='Input your message:', font=("Times New Roman", 18))
    msg_label.pack(padx=30, pady=5, anchor='w')
    msg = ctk.CTkTextbox(msg_frame, width=560, height=300)
    msg.pack(padx=10, pady=5)
    msg_frame.pack(padx=20, pady=10, anchor=ctk.CENTER)


    send_button = ctk.CTkButton(master=email_frame, text='Send', width=80, command=handle_send)
    send_button.pack(side='left', padx=(30, 10), pady=10)
    win.mainloop()

if __name__ == "__main__":
    main()
