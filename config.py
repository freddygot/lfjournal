import os

class Config:
    SECRET_KEY = 'din_hemmelige_nøkkel_her'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///journalsystem.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
