import json
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import quote

adict = {"0": "A", "1": "B", "2": "C", "3": "D", "4": "E", "5": "F", "6": "G", "7": "H", "8": "I", "9": "J"}


@dataclass
class FilmInfo:
    fId: int
    title: str
    rateKp: float
    rateImdb: float
    bio: str
    year: int
    posterUrl: str


def serialize_url(url):
    class UrlReference:
        def __init__(self, url):
            self.url = url

        def __str__(self):
            return f"url({self.url})"

    return json.dumps(UrlReference(url).__str__(), separators=(',', ':'))


def intersect_dicts(dict1, dict2):
    return {k: dict1[k] for k in dict1 if k in dict2 and dict1[k] == dict2[k]}


def port_to_code(port):
    port = str(port)
    res = ""
    for number in port:
        res += adict[number]
    return res + "\n"


def make_query(limit, sortField, genre_plus, yearFrom="default", yearTo="default", rateFrom="default", rateTo="default", genre_minus="default"):
    url = "https://api.kinopoisk.dev/v1.4/movie?"

    if not genre_minus:
        genre_minus = "default"

    if not yearFrom:
        yearFrom = "default"

    if not yearTo:
        yearTo = "default"

    if not rateFrom:
        rateFrom = "default"

    if not rateTo:
        rateTo = "default"

    limit_query = f"limit={limit}"

    selectField = ["id", "name", "year", "description", "poster", "rating", "genres"]
    select_query = ""
    for string in selectField:
        select_query += f"&selectFields={string}"

    notNullFields = ["id", "name", "year", "description", "poster.url", "rating.kp", "rating.imdb", "genres.name"]
    null_query = ""
    for string in notNullFields:
        null_query += f"&notNullFields={string}"

    sort_query = f"sortField={sortField}"
    sort_type_query = f"sortType=1"
    status_query = f"status=completed"

    if yearTo == "default" and yearFrom != "default":
        NewYearTo = datetime.now().year
        year_query = f"year={yearFrom}-{NewYearTo}"
    elif yearTo != "default" and yearFrom == "default":
        year_query = f"year=1900-{yearTo}"
    elif yearTo == "default" and yearFrom == "default":
        NewyearTo = datetime.now().year
        year_query = f"year=1900-{NewyearTo}"
    elif yearTo != "default" and yearFrom != "default":
        if yearTo == yearFrom:
            year_query = f"year={yearFrom}"
        else:
            year_query = f"year={yearFrom}-{yearTo}"

    if rateFrom != "default" and rateTo != "default":
        if rateFrom == rateTo:
            rate_query = f"rating.kp={rateTo}"
        else:
            rate_query = f"rating.kp={rateFrom}-{rateTo}"
    if rateFrom == "default" and rateTo == "default":
        rate_query = f"rating.kp=5-10"
    if rateFrom != "default" and rateTo == "default":
        rate_query = f"rating.kp={rateFrom}-10"
    if rateFrom == "default" and rateTo != "default":
        rate_query = f"rating.kp=5-{rateTo}"

    if genre_minus == "default":
        genre_query = ""
        if len(genre_plus) == 1:
            genre_query = f"&genres.name={quote(genre_plus[0])}"

        else:
            for genre in genre_plus:
                genre_query += f"&genres.name=%2B{quote(genre)}"

    else:
        if len(genre_plus) == 1:
            genre_query = f"&genres.name=%2B{quote(genre_plus[0])}"
            for genre in genre_minus:
                genre_query += f"&genres.name=%21{quote(genre)}"

        else:
            genre_query = ""
            for genre in genre_plus:
                genre_query += f"&genres.name=%2B{quote(genre)}"
            for genre in genre_minus:
                genre_query += f"&genres.name=%21{quote(genre)}"

    query = "{0}{1}{2}{3}&{4}&{5}&{6}&{7}&{8}{9}".format(url, limit_query, select_query, null_query, sort_query,
                                                          sort_type_query,
                                                          status_query, year_query, rate_query, genre_query)
    return query


def extract_data(data):
    films = []
    for film in data['docs']:
        films.append(FilmInfo(film['id'], film['name'], film['rating']['kp'], film['rating']['imdb'], film['description'].rstrip('\r\n'), film['year'], film['poster']['url']))

    return films


def encode_data(data):
    film_jsons = []
    for film in data:
        film_jsons.append(json.dumps(asdict(film)))

    return film_jsons






