# coding=utf-8
import queue
import os
import re
import signal
import sys
import threading

import requests
from requests.exceptions import ConnectionError, Timeout, ConnectTimeout, ReadTimeout

from .parser import cfg_parser as cp, args_parser as ap
import multi_thread

SIZE_1_MB = 2 ** 20
SIZE_1_GB = 1024 * SIZE_1_MB
UNIT = SIZE_1_MB

lock = threading.Lock()

# 多线程需要的全局变量
url = ''
save_dir = ''
filename = ''
ovd_file = ''
size = 0
pieces = []
piece_cnt = 0
offset = 0


def create_file(f_name, _size):
    with open(f_name, 'wb') as f:
        f.seek(_size - 1)
        f.write(b'\x00')


def create_ovd(f_name, size_m):
    global pieces
    pieces = [0] * size_m
    b_url = bytes(url, encoding='utf8')
    length = 4 + len(b_url) + size_m
    create_file(f_name, length)
    with open(f_name, 'rb+') as f:
        f.write(len(b_url).to_bytes(2, 'big'))
        f.write(b_url)
        f.write(size_m.to_bytes(2, 'big'))


def read_ovd(f_name):
    global pieces, piece_cnt
    with open(f_name, 'rb') as f:
        data = f.read()
        length = int.from_bytes(data[offset - 2:offset], 'big')
        for i in range(offset, offset + length):
            if data[i] == 0:
                pieces.append(0)
            else:
                pieces.append(1)
                piece_cnt += 1


def head_url():
    global url
    r = requests.head(url)
    if 300 <= r.status_code < 400:
        # 这里只处理了使用headers的重定向
        url = r.headers['Location']
        r = head_url()
    return r


def get_ranges():
    global filename, ovd_file, offset
    r = head_url()
    f_size = int(r.headers['Content-Length'])
    # print(r.headers)

    ranges = []
    idx = 0
    while True:
        if idx + UNIT >= f_size:
            ranges.append((idx, f_size - 1))
            break
        ranges.append((idx, idx + UNIT - 1))
        idx += UNIT

    content_disposition = r.headers['Content-Disposition']
    filename = re.search('(?<=filename=").*(?=")', content_disposition).group()
    ovd_file = re.sub('\\.[a-zA-Z0-9]+?$', '.ovd', filename)
    offset = 4 + len(bytes(url, encoding='utf8'))

    if os.path.exists(save_dir + ovd_file) and os.path.exists(save_dir + filename):
        read_ovd(save_dir + ovd_file)
    else:
        create_file(save_dir + filename, f_size)
        create_ovd(save_dir + ovd_file, len(ranges))

    return ranges


def download_piece(dic):
    global piece_cnt

    sta_end = dic['sta_end']
    start = sta_end[0]
    end = sta_end[1]
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    # print(headers)
    content = None
    while not content:
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=10)
            content = r.content
        except (ConnectionError, Timeout, ConnectTimeout, ReadTimeout) as e:
            # print('%d %s' % (dic['index'], str(e)))
            pass

    with open(save_dir + filename, "rb+") as f:
        f.seek(start)
        f.write(content)
    with open(save_dir + ovd_file, 'rb+') as f:
        f.seek(offset + dic['index'])
        f.write(b'\xff')

    lock.acquire()
    piece_cnt += 1
    lock.release()

    print('\r\033[1;33mrate: %.2f%%\033[0m' % (piece_cnt / size * 100), end='')


def quit_all(_signal_num, _frame):
    print('\nYou can use the same command to continue download.')
    sys.exit(-1)


def queue_data(index, sta_end):
    return {'index': index, 'sta_end': sta_end}


def main(num):
    global size, pieces
    rs = get_ranges()

    q = queue.Queue()
    size = len(rs)

    # 部分视频的索引在片尾，先下载片尾20M
    last = 20

    for i in range(last):
        if pieces[i] == 0:
            q.put(queue_data(i, rs[i]))
        tmp = size - i - 1
        if pieces[tmp] == 0:
            q.put(queue_data(tmp, rs[tmp]))

    for i in range(last, size - last):
        if pieces[i] == 0:
            q.put(queue_data(i, rs[i]))

    multi_thread.start(num, q, download_piece)
    print('\ndone.')
    os.remove(save_dir + ovd_file)


if __name__ == '__main__':

    signal.signal(signal.SIGINT, quit_all)
    signal.signal(signal.SIGTERM, quit_all)

    arg = ap.parse_args()
    st_dir = arg[ap.ST_DIR]
    st_num = arg[ap.ST_NUM]
    setting_flag = st_dir or st_num

    if setting_flag is None and len(arg[ap.URL]) == 0:
        print('use \'python app.py -h\' or view README to get help')
        sys.exit(-1)

    if setting_flag is not None:
        if st_dir is not None:
            cp.set_item(cp.DIR, st_dir)
        if st_num is not None:
            cp.set_item(cp.NUM, st_num)

    if len(arg[ap.URL]) > 0:
        url = arg[ap.URL][0]
        save_dir = arg[ap.DIR] if arg[ap.DIR] else cp.get_dir()
        thread_num = arg[ap.NUM] if arg[ap.NUM] else cp.get_num()

        save_dir = save_dir.replace('\\', '/')
        if save_dir != '':
            if save_dir[-1] != '/':
                save_dir += '/'
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)

        print('--------------------------------')
        print('save directory:\t%s\nthread number:\t%d' % (save_dir, thread_num))

        # main
        main(thread_num)
