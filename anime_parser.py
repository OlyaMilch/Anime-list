from main import db, Anime, app
from fetch_anime import fetch_anime_data


def update_anime_info():
    with app.app_context():
        animes = Anime.query.filter(Anime.mal_id.isnot(None)).all()  # Get all anime with MAL ID
        print(f"Anime found for updates: {len(animes)}")

        for anime in animes:
            anime_data = fetch_anime_data(anime.mal_id)  # We receive data through a universal parser


            if anime_data is None:
                print(f"Loading error {anime.title}")
                continue

            print(f"Updating anime: {anime.title}")
            print(
                f"Year: {anime_data['year']}, Genre: {anime_data['genre']}, Rating: {anime_data['rating']}, Description: {anime_data['description']}")

            anime.description = anime_data['description']
            anime.rating = anime_data['rating']
            anime.genre = anime_data['genre']
            anime.year = anime_data['year']

            db.session.commit()
            print(f"Updated: {anime.title} ({anime_data['rating']})")


# Launching the update
if __name__ == '__main__':
    update_anime_info()
