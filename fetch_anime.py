import requests
from bs4 import BeautifulSoup


def fetch_anime_data(mal_id):

    # Requests data from MyAnimeList and parses the required information
    mal_url = f"https://myanimelist.net/anime/{mal_id}"
    response = requests.get(mal_url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code != 200:
        print(f"Loading error for MAL ID {mal_id}")
        return None  # Return None if there is an error

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1', class_='title-name')
    title = title_tag.text.strip() if title_tag else f'Unknown Title ({mal_id})'

    description_tag = soup.find('p', attrs={'itemprop': 'description'})
    description = description_tag.text.strip() if description_tag else "No description available."

    rating_tag = soup.find('div', class_='score-label')
    rating = float(rating_tag.text.strip()) if rating_tag and rating_tag.text.strip().replace('.', '', 1).isdigit() else None

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

    return {
        'title': title,
        'description': description,
        'rating': rating,
        'genre': genres,
        'year': year
    }
