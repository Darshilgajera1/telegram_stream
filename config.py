import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """ All the configurations and variable related to the script """
    DATABASE_USER = os.getenv('DATABASE_USERNAME')
    DATABASE_PASS = os.getenv('DATABASE_PASSWORD')
    DATABASE_READ_HOST = os.getenv('DATABASE_READ_HOSTNAME')
    DATABASE_PORT = int(os.getenv('DATABASE_PORT'))
