import requests
from bs4 import BeautifulSoup
from main import db, Anime, app

def update_anime_info():
    with app.app_context():
        animes = Anime.query.filter(Anime.mal_id.isnot(None)).all()  # Берём все аниме с MAL ID
        print(f"Найдено аниме для обновления: {len(animes)}")
        for anime in animes:
            mal_url = f"https://myanimelist.net/anime/{anime.mal_id}"  # Формируем ссылку

            response = requests.get(mal_url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                print(f"Ошибка загрузки {anime.title}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Получаем описание (оно находится в теге <p> внутри блока с классом 'description')
            description_tag = soup.find('p', attrs={'itemprop': 'description'})
            description = description_tag.text.strip() if description_tag else "Нет описания"

            # Получаем рейтинг (он находится в теге <div> с классом 'score-label')
            rating_tag = soup.find('div', class_='score-label')
            rating = float(rating_tag.text.strip()) if rating_tag else None

            # Получаем жанры (они в <span> внутри <div> с itemprop='genre')
            genre_tags = soup.find_all('span', attrs={'itemprop': 'genre'})
            genres = ', '.join([genre.text for genre in genre_tags]) if genre_tags else "Неизвестно"

            # Получаем год (он в <span> внутри блока с информацией)
            info_panel = soup.find('span', string="Aired:")
            if info_panel:
                year_text = info_panel.find_next_sibling(string=True).strip()
                year = int(year_text.split()[-1]) if year_text else None
            else:
                year = None

            # Обновляем базу
            anime.description = description
            anime.rating = rating
            anime.genre = genres
            anime.year = year

            db.session.commit()
            print(f"Обновлено: {anime.title} ({rating})")

# Запускаем обновление
if __name__ == '__main__':
    update_anime_info()
