import smtplib
import logging

# Import MIMEText, MIMEImage and MIMEMultipart module.
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import keyring

def sendMail(imagePath):

    gmail_user = keyring.get_password("ring", "gmail_user")
    gmail_password = keyring.get_password("ring", "gmail_user")

    try:
        body = "New appointments! Check website! <br>"
        # Define the source and target email address.
        strFrom = gmail_user
        #strTo = ["saavedra.edo@gmail.com", "Cemunozb@gmail.com", "Cemunozb@gmail.com", "teresitaarayaa@gmail.com"],
        strTo = []
        strTo.append(gmail_user)
        # Create an instance of MIMEMultipart object, pass 'related' as the constructor parameter.
        msgRoot = MIMEMultipart('related')
        # Set the email subject.
        msgRoot['Subject'] = "New appointments available"
        # Set the email from email address.
        msgRoot['From'] = strFrom
        # Set the email to email address.
        msgRoot['To'] = ", ".join(strTo)
        # Set the multipart email preamble attribute value. Please refer https://docs.python.org/3/library/email.message.html to learn more.
        msgRoot.preamble = '====================================================='
        # Create a 'alternative' MIMEMultipart object. We will use this object to save plain text format content.
        msgAlternative = MIMEMultipart('alternative')
        # Attach the bove object to the root email message.
        msgRoot.attach(msgAlternative)
        # Create a MIMEText object, this object contains the plain text content.
        msgText = MIMEText("New appointments! Check website!")
        # Attach the MIMEText object to the msgAlternative object.
        msgAlternative.attach(msgText)
        # Create a MIMEText object to contains the email Html content. There is also an image in the Html content. The image cid is image1.
        msgText = MIMEText('<b>'+body+'</b> <br/><br/>Su screenshot loco: <br/><img src="cid:image1"><br>', 'html')
        # Attach the above html content MIMEText object to the msgAlternative object.
        msgAlternative.attach(msgText)
        # Open a file object to read the image file, the image file is located in the file path it provide.
        fp = open(imagePath, 'rb')
        # Create a MIMEImage object with the above file object.
        msgImage = MIMEImage(fp.read())
        # Do not forget close the file object after using it.
        fp.close()
        # Add 'Content-ID' header value to the above MIMEImage object to make it refer to the image source (src="cid:image1") in the Html content.
        msgImage.add_header('Content-ID', '<image1>')
        # Attach the MIMEImage object to the email body.
        msgRoot.attach(msgImage)
        # Create an smtplib.SMTP object to send the email.
        # Send email with the smtp object sendmail method.
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.connect('smtp.gmail.com')
        #server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(strFrom, strTo, msgRoot.as_string())
        # server.close()
        server.quit()

    except Exception as e:
        logging.error("Something went wrong..." + str(e))
