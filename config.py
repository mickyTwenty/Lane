import configparser
from datetime import datetime

config_file = 'config.ini'

default_review_count = 250

global _App

class AppSettings:
    def __init__(self):
        self.SERVER_DIR = ''
        self.DOWNLOAD_DIR = ''

        self.REVIEW_COUNT = default_review_count

        self.load()
    
    def load(self):
        print('loading config.ini...')
        config = configparser.ConfigParser()

        config.read(config_file)

        self.SERVER_DIR = config['Settings']['SERVER_DIR']
        self.DOWNLOAD_DIR = config['Settings']['DOWNLOAD_DIR']

        self.REVIEW_COUNT = config['Settings'].getint('REVIEW_COUNT')
        if self.REVIEW_COUNT is None:
            self.REVIEW_COUNT = default_review_count

    def save(self):
        print('saving config.ini...')
        config = configparser.RawConfigParser()

        config.add_section('Settings')
        config.set('Settings', 'SERVER_DIR', self.SERVER_DIR)
        config.set('Settings', 'DOWNLOAD_DIR', self.DOWNLOAD_DIR)

        config.set('Settings', 'REVIEW_COUNT', self.REVIEW_COUNT)

        with open(config_file, 'w') as configfile:
            config.write(configfile)

class App:
    def __init__(self):
        self._Settings = AppSettings()

        self.USER_NAME = 'admin'
        self.USER_PASSWORD = 'Versatronics' + self.getDateTimeStamp('%d%m%y')

        self.APP_NAME = 'Versatronics Pty Ltd - Image Reviewer'

        self.img_path = './data/images/'
        self.review_path = "./reviewed/"

        self.REVIEW_STR = [
            'CORRECT',
            'WRONG',
            'FALSE',
            'DAMAGE'
        ]

        self.REVIEW_STYLE = [
            'border: 1px solid rgb(126, 126, 126);color: rgb(68, 156, 95)',
            'border: 1px solid rgb(126, 126, 126);color: rgb(183, 130, 99)',
            'border: 1px solid rgb(126, 126, 126);color: rgb(64, 71, 203)',
            'border: 1px solid rgb(126, 126, 126);color: rgb(11, 154, 214)',
        ]

        self.REVIEW_COLOR = [
            '#449c5f',
            '#b78263',
            '#4047cb',
            '#0b9ad6',
        ]



    def getDateTimeStamp(self, format):
        now = datetime.now()
        date_time = now.strftime(format)
        return date_time

_App = App()

