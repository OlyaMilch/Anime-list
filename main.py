from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)  # Flask instance handling requests. __name__ helps Flask understand the location of the application.

db_path = os.path.abspath('anime.db')  # Db path

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anime.db'  # "SQLALCHEMY_DATABASE_URI SQLALCHEMY_DATABASE_URI" — это специальное имя для пути к db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disabling change alerts from Flask
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Generate random secret key

db = SQLAlchemy(app)  # Binding SQLAlchemy to an application

# Contents inside db
class Anime(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mal_id = db.Column(db.Integer, unique=True, nullable=True)  # id for using anime parser
    description = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)

# Home page (shows anime list)
@app.route('/all')
def index():
    anime = Anime.query.all()  # Get all anime
    return render_template('index.html', anime=anime)

# Add anime page
@app.route('/add', methods=['GET', 'POST'])
def add_anime():
    if request.method == 'POST':
        title=request.form['title']
        year=request.form['year']
        genre=request.form['genre']
        rating=request.form['rating']
        description=request.form['description']
        new_anime = Anime(title=title)
        db.session.add(new_anime)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_anime.html')

# Anime edit page
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_anime(id):
    anime = Anime.query.get(id)
    if request.method == 'POST':
        anime.title = request.form['title']
        db.session.commit()
        return redirect(url_for('index'))  # Redirects the user to the home page

    return render_template('edit.html', anime=anime)

# Delete anime
@app.route('/delete/<int:id>')
def delete_anime(id):
    anime = Anime.query.get_or_404(id)
    db.session.delete(anime)
    db.session.commit()
    return redirect(url_for('index'))

# Launching the application
if __name__ == '__main__':
    with app.app_context():  # Needed for db to work
        db.create_all()  # Create db if it doesn't exist
    app.run(debug=True)
