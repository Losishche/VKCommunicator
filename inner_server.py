#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'grishaev'


import socket
from app_info import do_comment_photo, many_posts_wall_message
from app_info import get_important_params
from multiprocessing import Process, Queue
import io,sys
import time

class InnerServer():
    pass




class flushfile(object):
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()


class InnerServerConnections():
    #todo оформить классы соединений и сокетов через наследование!!!
    def __init__(self, port):

        self.port =port
        self.sock = socket.socket()
        self.sock.bind(('', self.port))
        self.sock.listen(2) #параметр - допустимое количество клиентов в очереди
        print('создали сокет!')

    #архитектура КАПеЦ, но зато поупражнялся с классами
    def accept_and_handling_client_for_photo_comment(self):

        self.conn, self.addr = self.sock.accept() #блокирует, сволочь, приложение
        #sys.stdout = flushfile(sys.stdout) #перенаправляем вывод в файл!!!!
        print('accepting ', self.port)
        self.data = self.conn.recv(1024)
        self.data= self.data.decode('utf8')
        print(self.data)
        state = True
        while state:
            try:
                if self.data=='start_commenting_photo':
                    self.conn.send(b'start_commenting_photo_resp')
                    print(self.data)
                    self.data = self.conn.recv(1024)
                    self.data=self.data.decode('utf8')
                    self.arg_list = self.data.split(',')
                    self.vk_group_id = self.arg_list[0]
                    api, postgres_con, postgres_cur = get_important_params()
                    self.generator_for_wall_posting = do_comment_photo(api, postgres_con, postgres_cur, self.vk_group_id, consider_user_sex=True, is_run_from_interface=True)
                    self.gen_result = None
                    while self.gen_result != 'handling_exception':
                        self.gen_result = next(self.generator_for_wall_posting)
                        print('Замораживается!?')
                    if self.gen_result == 'handling_exception':
                            self.conn.send(b'handling_exception')
                            self.conn, self.addr = self.restart_accepting_conn('photo')
                            print('handling_exception')
                            print(self.conn, self.addr)

                elif self.data=='catch_exception':
                    print(self.data)
                    self.conn.send(b'handling_exception')
                    self.inputed_captcha = self.conn.recv(1024)
                    self.inputed_captcha = self.inputed_captcha.decode('utf8')
                    print(self.inputed_captcha)
                    self.gen_result = self.generator_for_wall_posting.send(self.inputed_captcha)
                    #весь "рабочий" цикл идет внутри генератора!! сюда приходит, только если генератор "замораживается" ввиду ошибки (причем это 2-й и более exception)
                    while self.gen_result != 'handling_exception':
                        self.gen_result = next(self.generator_for_wall_posting)
                    if self.gen_result == 'handling_exception':
                            #print('наконец-то')
                            #conn.send(b'handling_exception')
                            self.conn, self.addr = self.restart_accepting_conn('photo')

                elif self.data=='ok':
                    self.conn.send(b'end')
                    self.conn, self.addr = self.restart_accepting_conn('photo')
                else:
                    print(self.data)
                    print('передан неизвестный параметр', self.data)
                    self.conn.send(b'unknown_parameter')
                    self.conn, self.addr = self.restart_accepting_conn('photo')
                #except vk.exceptions.VkAPIError:
                    #print('captcha exception again')
                    #conn.send(b'end_of_sending')
                    #conn, addr = restart_accepting_conn(conn, sock)
                #except StopIteration:
                    #conn.send(b'end_of_sending')
                    #print('Stop_iteration')
                    #conn, addr = restart_accepting_conn(conn, sock)
            except StopIteration:
                print('цикл отсылки завершился')
                self.conn.send(b'end')
                self.conn, self.addr = self.restart_accepting_conn('photo')


    def accept_and_handling_client_for_wall_comment(self):

        self.conn, self.addr = self.sock.accept() #блокирует, сволочь, приложение
        print('accepting ', self.port)
        self.data = self.conn.recv(1024)
        self.data=self.data.decode('utf8')
        print('for_wall', self.data)

        while True:

            try:
                if self.data=='start_posting_wall_comments':
                    self.conn.send(b'start_posting_wall_comments_resp')
                    self.data = self.conn.recv(1024)
                    self.data=self.data.decode('utf8')
                    arg_list = self.data.split(',')
                    vk_group_id = arg_list[0]
                    print('args:', arg_list)
                    print(vk_group_id)
                    api, postgres_con, postgres_cur = get_important_params()
                    self.generator_for_wall_posting = many_posts_wall_message(api, postgres_con, postgres_cur, vk_group_id, is_run_from_interface=True)
                    #many_posts_wall_message(api, postgres_con, postgres_cur, vk_group_id)
                    gen_result = None
                    while gen_result != 'handling_exception_captcha needed': #этот сигнал является сигналом генератора, а не внутреннего сервера!
                        gen_result = next(self.generator_for_wall_posting)
                        print('генератор постов на стенки замораживается!')
                    if gen_result == 'handling_exception_captcha needed': #ОБРАБОТКА ГЕНЕРАТОРОМ КАПЧИ!!
                            self.conn.send(b'handling_exception')
                            self.conn, self.addr = self.restart_accepting_conn('wall')


                elif self.data=='catch_exception':
                    print(self.data)
                    self.conn.send(b'handling_exception')
                    inputed_captcha = self.conn.recv(1024)
                    inputed_captcha = inputed_captcha.decode('utf8')
                    print(inputed_captcha)
                    gen_result = self.generator_for_wall_posting.send(inputed_captcha)
                    #весь "рабочий" цикл идет внутри генератора!! сюда приходит, только если генератор "замораживается" ввиду ошибки (причем это 2-й и более exception)
                    #б..ьб!! именно, второй и более эксепшн
                    while gen_result != 'handling_exception_captcha needed':
                        gen_result = next(self.generator_for_wall_posting)
                    if gen_result == 'handling_exception_captcha needed':
                            #print('наконец-то')
                            #conn.send(b'handling_exception')
                            self.conn, self.addr = self.restart_accepting_conn('wall')

                elif self.data=='ok':
                    self.conn.send(b'end_wall_posting')
                    self.conn, self.addr = self.restart_accepting_conn('wall')
                else:
                    self.conn.send(b'unknown_parameter')
                    self.conn, self.addr = self.restart_accepting_conn('wall')
                #except vk.exceptions.VkAPIError:
                    #print('captcha exception again')
                    #conn.send(b'end_of_sending')
                    #conn, addr = restart_accepting_conn(conn, sock)
                #except StopIteration:
                    #conn.send(b'end_of_sending')
                    #print('Stop_iteration')
                    #conn, addr = restart_accepting_conn(conn, sock)
            except StopIteration:
                print('цикл отсылки завершился')
                self.conn.send(b'end_wall_posting')
                self.conn, self.addr = self.restart_accepting_conn('wall')


    def restart_accepting_conn(self, kind_of_connection):
        if kind_of_connection=='photo':
            self.conn.close()
            self.accept_and_handling_client_for_photo_comment()
        elif kind_of_connection=='wall':
            self.conn.close()
            self.accept_and_handling_client_for_wall_comment()
        #self.conn, self.addr = self.sock.accept()
        #return self.conn, self.addr



def running_server(queue, port, kind_of_socket):
#здесь первым параметром обзательно должен быть queue
   instance =  InnerServerConnections(port)
   if kind_of_socket=='photo':
       print('поднимаем сокет для photo')
       instance.accept_and_handling_client_for_photo_comment()

   elif kind_of_socket=='wall':
       print('поднимаем сокет для wall')
       instance.accept_and_handling_client_for_wall_comment()

   return instance



queue = Queue()
allProcess = []

def sockets_with_multiproc(count=2):
    """
    """
    count_of_sockets = 0
    port = 9091
    target = ''
    kind_of_socket= ['photo', 'wall']
    while count_of_sockets < count:
        #идем по списку портов начиная с заданного, если порт свободен, инициализируем сокет по данному адресу и порту
        # в случае успеха, на следующей итерации начнётся проверка с того, который был инициализирован на прошлой итерации
        targetIP = socket.gethostbyname(target)
        result = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while not result:
            result = s.connect_ex((targetIP, port))
            print('Port {} is already open'.format(port))
            port += 1

        print('established_port: {}'.format(port))
        print(s.close())
        p = Process(target = running_server, args=(queue, port, kind_of_socket[count_of_sockets]))
        allProcess.append(p)
        count_of_sockets += 1
        print('создали процесс для сокета!')

    for p in allProcess:
        p.start()
    print(allProcess)


if __name__ =='__main__':
    sockets_with_multiproc()

'''

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(2) #параметр - допустимое количество клиентов в очереди
conn, addr = sock.accept()

def restart_accepting_conn(conn, sock):
    conn.close()
    conn, addr = sock.accept()
    return conn, addr

print('connected:', addr)

#def running_server():
status = True
while status:

    data = conn.recv(1024)
    data=data.decode('utf8')
    print(data)
    try:
        if data=='start_commenting_photo':
            conn.send(b'start_commenting_photo_resp')
            data = conn.recv(1024)
            data=data.decode('utf8')
            arg_list = data.split(',')
            vk_group_id = arg_list[0]
            api, postgres_con, postgres_cur = get_important_params()
            generator_for_commenting = do_comment_photo(api, postgres_con, postgres_cur, vk_group_id, consider_user_sex=True, is_run_from_interface=True)
            gen_result = None
            while gen_result != 'handling_exception':
                gen_result = next(generator_for_commenting)
                print('Замораживается!?')
            if gen_result == 'handling_exception':
                    conn.send(b'handling_exception')
                    conn, addr = restart_accepting_conn(conn, sock)

        elif data=='catch_exception':
            print(data)
            conn.send(b'handling_exception')
            inputed_captcha = conn.recv(1024)
            inputed_captcha = inputed_captcha.decode('utf8')
            print(inputed_captcha)
            gen_result = generator_for_commenting.send(inputed_captcha)
            #весь "рабочий" цикл идет внутри генератора!! сюда приходит, только если генератор "замораживается" ввиду ошибки (причем это 2-й и более exception)
            while gen_result != 'handling_exception':
                gen_result = next(generator_for_commenting)
            if gen_result == 'handling_exception':
                    #print('наконец-то')
                    #conn.send(b'handling_exception')
                    conn, addr = restart_accepting_conn(conn, sock)

        elif data=='ok':
            conn.send(b'end')
            conn, addr = restart_accepting_conn(conn, sock)
        else:
            conn.send(b'unknown_parameter')
            conn, addr = restart_accepting_conn(conn, sock)
        #except vk.exceptions.VkAPIError:
            #print('captcha exception again')
            #conn.send(b'end_of_sending')
            #conn, addr = restart_accepting_conn(conn, sock)
        #except StopIteration:
            #conn.send(b'end_of_sending')
            #print('Stop_iteration')
            #conn, addr = restart_accepting_conn(conn, sock)
    except StopIteration:
        print('цикл отсылки завершился')
        conn.send(b'end')
        conn, addr = restart_accepting_conn(conn, sock)

sock.close()

#conn.close()
'''