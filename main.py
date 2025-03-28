from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import requests
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

# Add anime page
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

@app.route('/add_anime_form')
def add_anime_form():
    return render_template('add_anime_form.html')

@app.route('/add_anime', methods=['POST'])
def add_anime():
    data = request.get_json()

    if not data or 'mal_id' not in data:
        return jsonify({'error': 'mal_id is required'}), 400

    mal_id = data['mal_id']

    existing_anime = Anime.query.filter_by(mal_id=mal_id).first()
    if existing_anime:
        return jsonify({'message': 'Anime already exists in the database'}), 200

    mal_url = f"https://myanimelist.net/anime/{mal_id}"
    response = requests.get(mal_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from MyAnimeList'}), 500

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1', class_='title-name')
    title = title_tag.text.strip() if title_tag else f'Unknown Title ({mal_id})'

    description_tag = soup.find('p', attrs={'itemprop': 'description'})
    description = description_tag.text.strip() if description_tag else "No description available."

    rating_tag = soup.find('div', class_='score-label')
    rating = float(rating_tag.text.strip()) if rating_tag and rating_tag.text.strip().replace('.', '',
                                                                                              1).isdigit() else None

    genre_tags = soup.find_all('span', attrs={'itemprop': 'genre'})
    genres = ', '.join([genre.text for genre in genre_tags]) if genre_tags else "Unknown"

    year = None
    info_panel = soup.find('span', string="Aired:")
    if info_panel:
        year_text = info_panel.find_next_sibling(string=True).strip()
        try:
            year = int(year_text.split()[-1]) if year_text and year_text.strip() != "?" else None
        except ValueError:
            year = None

    new_anime = Anime(
        title=title,
        mal_id=mal_id,
        description=description,
        rating=rating,
        genre=genres,
        year=year
    )

    try:
        db.session.add(new_anime)
        db.session.commit()
        print('Anime added successfully')
    except Exception as e:
        print("Database Error", e)
    return jsonify({'message': 'Anime successfully added!', 'anime': {'title': title, 'mal_id': mal_id}}), 201


# Launching the application
if __name__ == '__main__':
    with app.app_context():  # Needed for db to work
        db.create_all()  # Create db if it doesn't exist
    app.run(debug=True)
