#-------------------------------------
# Import Modules
#-------------------------------------
import pandas as pd
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def main_func():
    #-------------------------------------
    # Define Email Header
    #-------------------------------------
    fromaddr = "w.glaeser@xxxxxxx"
    #toaddr = "xxx,xxx,xxx"
    toaddr = 'xxx'
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr

    #-------------------------------------
    # Check for new Emails
    #-------------------------------------
    scrape_path = '/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/individual_scrape/'
    all_scrapes = os.listdir(scrape_path)
    all_csv = [f for f in all_scrapes if 'csv' in f]
    filename = sorted(all_csv)[len(all_csv)-1]

    df = pd.read_csv('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/' \
                 'individual_scrape/' + filename, encoding='latin-1')
    new_flats = len(df)

    #-------------------------------------
    # Email Body
    #-------------------------------------
    body = "Moin ihr lutscher,\n\n" \
           "Es gibt wundervolle Neuigkeiten! Es ist/sind " \
           "{} neue Wohnungen erschienen! Checks aus.\n\n"\
           "See you later".format(new_flats)
    msg['Subject'] = "Es gihihibt neue Wohnungen"

    #-------------------------------------
    # Email Attachment
    #-------------------------------------
    msg.attach(MIMEText(body, 'plain'))

    filename = "properties_full.xlsx"
    attachment = open("/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/properties_full.xlsx", "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    #-------------------------------------
    # Configure Server and Send
    #-------------------------------------
    if new_flats > 0:
        server = smtplib.SMTP('smtp.office365.com',587)
        server.starttls()
        server.login(fromaddr, "passwd")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr.split(','), text)
        server.quit()
        print('There were new properties. Email has been sent.')
    elif new_flats == 0:
        print('There were no new flats.')
