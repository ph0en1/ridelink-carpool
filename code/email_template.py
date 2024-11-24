import smtplib #(simple mail transfer protocol)
import ssl #(secure socket layer)
from email.message import EmailMessage

sender="centralized@gmail.com"
receiver="udyat.m@gmail.com"
password="sscy uadp heop pdox"

port=465
domain="smtp.gmail.com"

message=EmailMessage()
message["From"]=sender
message["To"]=receiver
message["Subject"]="Hello there."
message.set_content('''Hello there.
How are you doing?
Thanks,
Udyat
''')

context=ssl.create_default_context() 
for i in range(3):  #not necessary
  with smtplib.SMTP_SSL(domain,port,context=context) as server:
    server.login(sender,password)
    server.send_message(message,from_addr=sender,to_addrs=receiver)
    print("Email sent")
