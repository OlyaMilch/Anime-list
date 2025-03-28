# from flask import request, jsonify
# from main import db, Anime, app
# import requests
# from bs4 import BeautifulSoup
#
#
# """
# Thanks to this, the parser searches for anime by mal_id.
# If the anime is not in the db, a new record is created.
# If the anime is in the db, the data is updated.
# """
#
# # Add anime using mal_id
# @app.route('/add_anime', methods=['POST'])
# def add_anime():
#     data = request.get_json()
#     print("Received data:", data)
#     mal_id = data.get('mal_id')
#
#     if not mal_id:
#         return jsonify({'error': 'mal_id is required'}), 400
#
#     # Проверяем, нет ли уже такого аниме в базе
#     existing_anime = Anime.query.filter_by(mal_id=mal_id).first()
#     if existing_anime:
#         return jsonify({'message': 'Anime already exists in the database'}), 200
#
#     # Формируем URL для парсинга
#     mal_url = f"https://myanimelist.net/anime/{mal_id}"
#     response = requests.get(mal_url, headers={"User-Agent": "Mozilla/5.0"})
#
#     if response.status_code != 200:
#         return jsonify({'error': 'Failed to fetch data from MyAnimeList'}), 500
#
#     soup = BeautifulSoup(response.text, 'html.parser')
#
#     # Получаем название аниме
#     title_tag = soup.find('h1', class_='title-name')
#     title = title_tag.text.strip() if title_tag else f'Unknown Title ({mal_id})'
#
#     # Получаем описание
#     description_tag = soup.find('p', attrs={'itemprop': 'description'})
#     description = description_tag.text.strip() if description_tag else "No description available."
#
#     # Получаем рейтинг
#     rating_tag = soup.find('div', class_='score-label')
#     rating = float(rating_tag.text.strip()) if rating_tag and rating_tag.text.strip().replace('.', '', 1).isdigit() else None
#
#     # Получаем жанры
#     genre_tags = soup.find_all('span', attrs={'itemprop': 'genre'})
#     genres = ', '.join([genre.text for genre in genre_tags]) if genre_tags else "Unknown"
#
#     # Получаем год выпуска
#     info_panel = soup.find('span', string="Aired:")
#     if info_panel:
#         year_text = info_panel.find_next_sibling(string=True).strip()
#         try:
#             year = int(year_text.split()[-1]) if year_text and year_text.strip() != "?" else None
#         except ValueError:
#             year = None
#     else:
#         year = None
#     with app.app_context():  # Добавляем контекст приложения
#         existing_anime = Anime.query.filter_by(mal_id=mal_id).first()
#         if existing_anime:
#             return jsonify({'message': 'Anime already exists in the database'}), 200
#
#     # Создаем новый объект аниме
#     new_anime = Anime(
#         title=title,
#         genre=genres,
#         year=year,
#         mal_id=mal_id,
#         description=description,
#         rating=rating
#     )
#
#     db.session.add(new_anime)
#     db.session.commit()
#
#     return jsonify({
#         'message': 'Anime successfully added!',
#         'anime': {
#             'title': title,
#             'genre': genres,
#             'year': year,
#             'mal_id': mal_id,
#             'description': description,
#             'rating': rating
#         }
#     }), 201
#
# if __name__ == '__main__':
#     app.run(debug=True)