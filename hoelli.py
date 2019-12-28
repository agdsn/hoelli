import gevent
from gevent import monkey
monkey.patch_socket()

import random
import socket
import time
import urllib.request


N_GREENLETS = 16
DT_OFFSET = 20.0
DT_IMG = 60.0


def get_offset(px_cnt=0):
    # load offset
    url = 'http://hoellipixelflut.de/xy/?report={px_cnt}'.format(px_cnt=px_cnt)
    offset = urllib.request.urlopen(url).read()

    x, y = offset.decode().split()
    print('New offset: ', x, y)
    return int(x), int(y)


def get_img():
    lines = urllib.request.urlopen(
        'http://hoellipixelflut.de/hoelli.csv').read()
    lines = lines.decode('utf-8').split('\n')[:-1]

    img = []
    for line in lines:
        img.append(line.replace(' ', '').split(','))

    h = len(img)
    w = len(img[0])

    return img, w, h


def bombard():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('151.217.111.34', 1234))

    dx, dy = get_offset()
    print(dx, dy)

    img, w, h = get_img()
    print(w, h)

    print('Start...')
    time0 = 0
    time1 = 0
    i_sock = 0
    px_cnt = 0
    i = 0
    while True:
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)

        rgb = img[y][x]
        if rgb == '000000':
            continue

        cmd = 'PX {xx} {yy} {rgb}\n'.format(xx=x+dx, yy=y+dy, rgb=rgb).encode()
        sockets[i_sock].send(cmd)
        px_cnt += 1
        i_sock = (i_sock + 1) % N_GREENLETS

        if i % 1024 == 0:
            if time.time() - time0 > DT_OFFSET:
                dx, dy = get_offset(px_cnt)
                time0 = time.time()
                px_cnt = 0

            if time.time() - time1 > DT_IMG:
                print('Update Image')
                img, w, h = get_img()
                time1 = time.time()
        i += 1


def main():
    greenlets = [gevent.spawn(bombard) for _ in range(N_GREENLETS)]
    gevent.joinall(greenlets)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(e)
