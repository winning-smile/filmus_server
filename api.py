import json
import requests
from datetime import datetime

#with open('data.txt') as json_file:
    #data = json.load(json_file)

#ndata = json.dumps(data, indent=4)
#for film in data['docs']:
#    print(film['id'])
#    print(film['name'])
#    print(film['genres'])

#print(data['docs'][0]['id'])

# data['docs'][0]['id']
# NAME data['docs'][0]['name']
#

def make_query(limit, sortField, yearFrom, yearTo, rateFrom, rateTo, genre_plus, genre_minus):
    url = "https://api.kinopoisk.dev/v1.4/movie?"
    api_token = "CV8TT3N-4T547VH-HEWCBQP-TRRHEBE"
    api_header = {"X-API-KEY": api_token}

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
        year_query = f"year=1000-{yearTo}"
    elif yearTo == "default" and yearFrom == "default":
        NewyearTo = datetime.now().year
        year_query = f"year={yearFrom}-{NewyearTo}"
    elif yearTo != "default" and yearFrom != "default":
        year_query = f"year={yearFrom}-{yearTo}"

    if rateFrom != "default" and rateTo != "default":
        rate_query = f"rating.kp={rateFrom}-{rateTo}"
    if rateFrom == "default" and rateTo == "default":
        rate_query = f"rating.kp=5-10"
    if rateFrom != "default" and rateTo == "default":
        rate_query = f"rating.kp={rateFrom}-10"
    if rateFrom == "default" and rateTo != "default":
        rate_query = f"rating.kp=5-{rateTo}"

    if genre_minus == "default":
        genre_query = ""
        if genre_plus.len() == 1:
            genre_query = f"&genres.name={genre_plus}"

        else:
            for genre in genre_plus:
                genre_query += f"&genres.name=+{genre}"

    else:
        if genre_plus.len() == 1:
            genre_query = f"&genres.name=+{genre_plus}"
            for genre in genre_minus:
                genre_query += f"&genres.name=+{genre}"

        else:
            genre_query = ""
            for genre in genre_plus:
                genre_query += f"&genres.name=+{genre}"
            for genre in genre_minus:
                genre_query += f"&genres.name=!{genre}"

    query = "{0}{1}{2}{3}&{4}&{5}&{6}&{7}&{8}&{9}".format(url, limit_query, select_query, null_query, sort_query,
                                                          sort_type_query,
                                                          status_query, year_query, rate_query, genre_query)
    print(query)












#request = requests.get(query, headers=api_header)
#
#print(request)
#print(request.json())
#print(request.text)

