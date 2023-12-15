import socket
import json
import requests
from _thread import *
from dataclasses import dataclass, asdict

adict = {"0": "A", "1": "B", "2": "C", "3": "D", "4": "E", "5": "F", "6": "G", "7": "H", "8": "I", "9": "J"}
film_dict = {"триллер": "1",
             "драма": "2",
             "криминал": "3",
             "мелодрама": "4",
             "детектив": "5",
             "фантастика": "6",
             "приключения": "7",
             "биография": "8",
             "фильм-нуар": "9",
             "вестерн": "10",
             "боевик": "11",
             "фэнтези": "12",
             "комедия": "13",
             "военный": "14",
             "история": "15",
             "музыка": "16",
             "ужасы": "17",
             "мультфильм": "18",
             "семейный": "19",
             "мюзикл": "20",
             "спорт": "21",
             "документальный": "22",
             "короткометражка": "23",
             "аниме": "24"}


@dataclass
class film_info:
    id: int
    name: str
    rate: float
    ratev2: float
    year: int
    poster_url: int

    def info(self):
        print(self.id, self.name, self.rate, self.ratev2, self.year, self.poster_url)


def serialize_url(url):
    class UrlReference:
        def __init__(self, url):
            self.url = url

        def __str__(self):
            return f"url({self.url})"

    return json.dumps(UrlReference(url).__str__(), separators=(',', ':'))

class FilmusServer:
    def __init__(self):
        self.films = []
        self.film_jsons = []
        self.host = "localhost"
        self.port = 6666
        self.thread_count = 0
        self.api_url = "https://kinopoiskapiunofficial.tech/api/v2.2/films?"
        self.api_token = "6a0de868-081f-4100-b6a2-d8aa65dd3296"
        self.api_header = {"X-API-KEY": self.api_token}
        self.api_req_data = []

        self.start_server(self.host, self.port)

    def clear_cache(self):
        self.films.clear()
        self.film_jsons.clear()
        self.api_req_data.clear()

    def client_handler(self, connection):
        data = connection.recv(2048)
        flag = data.decode()

        if flag  == "start":
            self.clear_cache()
            # ОТПРАВЛЯЕМ КОД ДЛЯ ПРИСОЕДИНЕНИЯ ВТОРОГО ЧЕЛОВЕКА (НА ОСНОВЕ ПОРТА)
            code = port_to_code(self.port)
            connection.sendall(code.encode())

            # ПРИНИМАЕМ ПАРАМЕТРЫ ДЛЯ API ЗАПРОСА
            data = connection.recv(2048)
            self.api_req_data = json.loads(data[2:].decode('utf-8'))
            print(self.api_req_data)

            # ПОЛУЧАЕМ СПИСОК ФИЛЬМОВ ИЗ API
            target_url = "{0}&genres={1}&order={2}&type=FILM&page=1".format(self.api_url,
                                                                            film_dict[self.api_req_data['genre']],
                                                                            str(self.api_req_data['sortType']))
            request = requests.get(target_url, headers=self.api_header)

            # КОНВЕРТИРУЕМ JSON В ЭКЗЕМПЛЯРЫ ДАТАКЛАССА ДЛЯ КАЖДОГО ФИЛЬМА
            for film in request.json()['items']:
                self.films.append(film_info(film['kinopoiskId'], film['nameRu'], film['ratingKinopoisk'],
                                            film['ratingImdb'], film['year'], int(film['posterUrl'][54:-4])))

            # СОБИРАЕМ JSON МАССИВ ДЛЯ ОТПРАВКИ КЛИЕНТУ
            for film in self.films:
                self.film_jsons.append(json.dumps(asdict(film)))

            # ОТПРАВЛЯЕМ JSON'Ы КЛИЕНТУ
            for film in self.film_jsons:
                print(film)
                connection.sendall(film.encode())

            connection.close()

        elif flag == "join":
            for film in self.film_jsons:
                print(film)
                connection.sendall(film.encode())

            connection.close()

        elif flag == "result":
            data = connection.recv(2048)
            print(data.decode())
            print(json.loads(data[2:].decode('utf-8')))

    def accept_connections(self, server_socket):
        client, address = server_socket.accept()
        print(f'Connected to: {address[0]}:{str(address[1])}')
        start_new_thread(self.client_handler, (client,))

    def start_server(self, host, port):
        server_socket = socket.socket()
        try:
            server_socket.bind((host, port))
        except socket.error as e:
            print(str(e))
        print(f'Server is listing on the port {port}...')
        server_socket.listen()

        while True:
            self.accept_connections(server_socket)
            #if self.thread_count == 2:
                #break


def port_to_code(port):
    port = str(port)
    res = ""
    for number in port:
        res += adict[number]
    return res + "\n"


if __name__ == '__main__':
    Server = FilmusServer()
