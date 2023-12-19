import socket
import requests
from _thread import *
from api import *


class FilmusServer:
    def __init__(self):
        self.films = []
        self.film_jsons = []
        self.host = "192.168.0.12"
        self.port = 50000
        self.thread_count = 0
        self.api_token = "CV8TT3N-4T547VH-HEWCBQP-TRRHEBE"
        self.api_header = {"X-API-KEY": self.api_token}
        self.first_data = []
        self.second_data = []
        self.solo_data = []
        self.result = []
        self.res_film_jsons = []
        self.clients = []
        self.ready = 0

        self.start_server(self.host, self.port)

    def clear_cache(self):
        self.films.clear()
        self.film_jsons.clear()
        self.first_data.clear()
        self.second_data.clear()
        self.result.clear()
        self.res_film_jsons.clear()
        self.clients.clear()
        self.solo_data.clear()
        self.ready = 0

    def client_handler(self, connection):
            data = connection.recv(2048)
            flag = data.decode()

            if flag == "start":
                # ЧИСТИМ КЭШ
                self.clear_cache()
                # ОТПРАВЛЯЕМ КОД ДЛЯ ПРИСОЕДИНЕНИЯ ВТОРОГО ЧЕЛОВЕКА (НА ОСНОВЕ ПОРТА)
                code = port_to_code(self.port)
                connection.sendall(code.encode())

                # ПРИНИМАЕМ ПАРАМЕТРЫ ДЛЯ API ЗАПРОСА
                data = connection.recv(2048)
                q_info = json.loads(data[2:].decode('utf-8'))
                print(q_info)

                # СОСТАВЛЯЕМ API ЗАПРОС
                query = make_query(q_info['limit'], q_info['sortField'], q_info['genrePlus'], q_info['yearFrom'], q_info['yearTo'],
                                   q_info['rateFrom'], q_info['rateTo'], q_info['genreMinus'])

                print(query)

                # ДЕЛАЕМ API ЗАПРОС
                info = self.make_request(query)
                # КОМПОНУЕМ ДАННЫЕ ИЗ API
                self.films = extract_data(info)
                # КОДИРУЕМ ДАННЫЕ ДЛЯ ОТПРАВКИ
                self.film_jsons = encode_data(self.films)
                # ОТПРАВЛЯЕМ ДАННЫЕ
                self.send_data(connection)
                connection.close()

            elif flag == "startSolo":
                # ЧИСТИМ КЭШ
                self.clear_cache()

                # ПРИНИМАЕМ ПАРАМЕТРЫ ДЛЯ API ЗАПРОСА
                data = connection.recv(2048)
                q_info = json.loads(data[2:].decode('utf-8'))

                # СОСТАВЛЯЕМ API ЗАПРОС
                query = make_query(q_info['limit'], q_info['sortField'], q_info['genrePlus'], q_info['yearFrom'], q_info['yearTo'],
                                   q_info['rateFrom'], q_info['rateTo'], q_info['genreMinus'])

                print(query)
                ## ДЕЛАЕМ API ЗАПРОС
                info = self.make_request(query)
                ## КОМПОНУЕМ ДАННЫЕ ИЗ API
                self.films = extract_data(info)
                print(info)
                ## КОДИРУЕМ ДАННЫЕ ДЛЯ ОТПРАВКИ
                self.film_jsons = encode_data(self.films)
                ## ОТПРАВЛЯЕМ ДАННЫЕ
                self.send_data(connection)
                connection.close()

            elif flag == "join":
                print("second device connected")
                self.send_data(connection)
                connection.close()

            elif flag == "ready":
                print("READY")
                self.ready += 1

            elif flag == "ready2":
                while self.ready != 2:
                    pass
                connection.sendall("ready".encode())

            elif flag == "result":
                data = connection.recv(2048)
                if not self.first_data:
                    self.first_data = json.loads(data[2:].decode('utf-8'))
                    print("first data recieved")
                    print(self.first_data)
                else:
                    self.second_data = json.loads(data[2:].decode('utf-8'))
                    print("second data recieved")
                    print(self.second_data)

            elif flag == "resultSolo":
                data = connection.recv(2048)
                self.solo_data = json.loads(data[2:].decode('utf-8'))

            elif flag == "final":
                self.clients.append(connection)

                if self.first_data and self.second_data:
                    first = {key: val for key, val in self.first_data.items() if val == "Right"}
                    second = {key: val for key, val in self.second_data.items() if val == "Right"}
                    final = intersect_dicts(first, second)

                    for film in self.films:
                        for key in final.keys():
                            if str(film.fId) == str(key):
                                print(f"id={film.fId}, key={key}")
                                self.result.append(film)

                    for film in self.result:
                        self.res_film_jsons.append(json.dumps(asdict(film)))

                    for conn in self.clients:
                        for film in self.res_film_jsons:
                            print(f"data send to {conn}")
                            conn.sendall(film.encode())

                        conn.close()

            elif flag == "finalSolo":
                solo = {key: val for key, val in self.solo_data.items() if val == "Right"}

                for film in self.films:
                    for key in solo.keys():
                        if str(film.fId) == str(key):
                            print(f"id={film.fId}, key={key}")
                            self.result.append(film)

                for film in self.result:
                    self.res_film_jsons.append(json.dumps(asdict(film)))

                for film in self.res_film_jsons:
                    print(f"data send to {connection}")
                    connection.sendall(film.encode())

                connection.close()

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

    def make_request(self, query):
        request = requests.get(query, headers=self.api_header)
        return request.json()

    def send_data(self, connection):
        for film in self.film_jsons:
            connection.sendall(film.encode())



if __name__ == '__main__':
    Server = FilmusServer()
