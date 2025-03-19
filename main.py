from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)  # Flask instance handling requests. __name__ helps Flask understand the location of the application.

db_path = os.path.abspath('anime.db')  # Db path

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anime.db'  # "SQLALCHEMY_DATABASE_URI SQLALCHEMY_DATABASE_URI" — это специальное имя для пути к db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disabling change alerts from Flask
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Generate random secret key

db = SQLAlchemy(app)  # Binding SQLAlchemy to an application


