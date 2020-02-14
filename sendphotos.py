#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
A script than sends emails with photos that is supposed to run continuously.

Uses photoconfig.yaml for SMTP settings and locations of files with addresses and photo locations.
Names of the files are e-mail addresses and their content are paths to images sent to the address.
'''

import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

import yaml

from photologging import Logging

log = Logging()


class Sending:

    def __init__(self, config=None):

        # globals1
        path = os.path.dirname(os.path.realpath(__file__))
        if not config:
            with open("photoconfig.yaml", 'r') as stream:
                config = yaml.full_load(stream)
        self.config = config
        self.filelistdir = os.path.join(path, config['paths']['addr'])
        self.photodir = os.path.join(path, config['paths']['photopath'])
        emailpath = os.path.join(path, config['paths']['emailmessage'])
        with open(emailpath, 'r') as stream:
            self.emailmessage = stream.read()

    def smtp_connect(self):
        smtpserver = 'smtp.' + self.config['smtp']['domain'] + ':465'
        server = smtplib.SMTP_SSL(smtpserver)
        server.ehlo()
        server.login(self.config['smtp']['login'], self.config['smtp']['password'])
        return server

    def create_message(self, filelistpath=""):
        log.append(filelistpath)
        if not os.path.isfile(filelistpath):
            log.append("file %s not exist" % filelistpath)
            return ""

        log.append("recipient " + os.path.split(filelistpath)[1])
        outer = MIMEMultipart()
        outer['Subject'] = 'Zdjęcia z Pikniku Naukowego'
        outer['To'] = os.path.split(filelistpath)[1]
        outer['From'] = self.config['smtp']['login'] + '@' + self.config['smtp']['domain']
        outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        with open(filelistpath, "r") as file:
            lines = file.read().splitlines()
        lines = [os.path.join(self.photodir, x.strip()) for x in lines if x.strip()]
        if not lines:
            return ""

        for path in lines:
            log.append("adding %s to email" % path)
            if not os.path.exists(path):
                continue
            ctype = "image/jpg"
            maintype, subtype = ctype.split('/', 1)
            with open(path, 'rb') as fp:
                msg = MIMEImage(fp.read(), _subtype=subtype)
                # Set the filename parameter
                msg.add_header('Content-Disposition', 'attachment', filename=os.path.split(path)[-1])
                outer.attach(msg)
            log.append("file " + path + " added")
        body = MIMEText(self.emailmessage, 'html')
        outer.attach(body)
        composed = outer.as_string()
        return composed

    def delete_files(self, filelistpath):
        if not os.path.exists(filelistpath):
            return
        log.append("deleting " + filelistpath)
        with open(filelistpath, "r") as file:
            lines = file.read().splitlines()
        lines = [os.path.join(self.photodir, x.strip()) for x in lines if x.strip()]
        for path in lines:
            if os.path.exists(path):
                os.remove(path)
        os.remove(filelistpath)

    def get_filename(self, filelist):
        log.append("get filename")
        for file in filelist:
            if file.strip()[0:8] == "!garbage":
                log.append("garbage!")
                filepath = os.path.join(self.filelistdir, file)
                self.delete_files(filepath)
                continue
            if file.strip()[0] != "!":
                return file
        return ""

    def serverconnect(self):
        server = None
        while not server:
            try:
                log.append("connecting")
                server = self.smtp_connect()
            except smtplib.SMTPException as e:
                log.append(" ".join(str(e).splitlines()))
                sleep(1)
            except OSError as e:
                log.append(" ".join(str(e).splitlines()))
                sleep(10)
        return server

    def run(self):
        while True:
            log.append("sendphotos")
            sleep(0.5)
            filename = self.get_filename(os.listdir(self.filelistdir))
            log.append(filename)
            if filename:
                server = self.serverconnect()
                filelistpath = os.path.join(self.filelistdir, filename)
                composed = self.create_message(filelistpath)
                try:
                    if composed:
                        log.append("sending to " + filename)
                        server.sendmail(self.config['smtp']['login'] + '@' + self.config['smtp']['domain'],
                                        filename, composed)
                        self.delete_files(filelistpath)
                    else:
                        log.append("not composed")
                        new_filelistpath = os.path.join(self.filelistdir, "!" + filename)
                        os.rename(filelistpath, new_filelistpath)
                except smtplib.SMTPServerDisconnected as e:
                    log.append(" ".join(str(e).splitlines()))
                    continue
                except smtplib.SMTPRecipientsRefused as e:
                    log.append(" ".join(str(e).splitlines()))
                    self.delete_files(filelistpath)
                    continue
                except OSError as e:
                    log.append(" ".join(str(e).splitlines()))
                    continue
                except Exception as e:
                    log.append(" ".join(str(e).splitlines()))
                    continue
                server.quit()


if __name__ == '__main__':
    Sending().run()
