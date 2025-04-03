from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from fetch_anime import fetch_anime_data
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
    year = db.Column(db.Integer, nullable=True)
    mal_id = db.Column(db.Integer, unique=True, nullable=True)  # id for using anime parser
    description = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)

# Home page (shows anime list)
@app.route('/all')
def index():
    anime = Anime.query.all()  # Get all anime
    return render_template('index.html', anime=anime)

# Add anime page. Without this the main page will not work
@app.route('/add', methods=['GET', 'POST'])
def add_new_anime():
    if request.method == 'POST':
        print(request.form)
        title=request.form.get('title')
        genre=request.form.get('genre')
        year=request.form.get('year', type=int)
        mal_id = int(request.form['mal_id'])
        description=request.form.get('description', '').strip()
        rating=request.form.get('rating', type=float)
        new_anime = Anime(title=title, genre=genre, year=year,
                           mal_id=mal_id, description=description, rating=rating)
        db.session.add(new_anime)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_anime.html')


# Delete anime
@app.route('/delete/<int:mal_id>')
def delete_anime(mal_id):
    anime = Anime.query.get_or_404(mal_id)
    db.session.delete(anime)
    db.session.commit()
    return redirect(url_for('index'))

# Returns the HTML page add_anime_form.html where we enter mal_id
@app.route('/add_anime_form')
def add_anime_form():
    return render_template('add_anime_form.html')


"""
Inside this function is a parser that:
1. Finds mal_id on the anime site.
2. Checks if the anime is in the database.
3. Generates a URL to MyAnimeList.
4. Sends a request and gets the anime HTML page.
5. Searches for the required data
"""


@app.route('/add_anime', methods=['POST'])
def add_anime():
    data = request.get_json()  # Converts an HTTP request into a Python dictionary

    if not data or 'mal_id' not in data:  # Checking if the data has arrived
        return jsonify({'error': 'mal_id is required'}), 400

    mal_id = data['mal_id']  # Takes the value of the key "mal_id".

    existing_anime = Anime.query.filter_by(mal_id=mal_id).first()
    if existing_anime:
        return jsonify({'message': 'Anime already exists in the database'}), 200

    anime_data = fetch_anime_data(mal_id)

    new_anime = Anime(
        title=anime_data['title'],
        mal_id=mal_id,
        description=anime_data['description'],
        rating=anime_data['rating'],
        genre=anime_data['genre'],
        year=anime_data['year']
    )

    try:
        db.session.add(new_anime)
        db.session.commit()
        print('Anime added successfully')
    except Exception as e:
        print("Database Error", e)
    return jsonify({'message': 'Anime successfully added!', 'anime': {'title': anime_data['title'], 'mal_id': mal_id}}), 201


# Launching the application
if __name__ == '__main__':
    with app.app_context():  # Needed for db to work
        db.create_all()  # Create db if it doesn't exist
    app.run(debug=True)
