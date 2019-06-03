# coding=utf-8


def create_odl_file(filename, url, size_mb):
    url_bytes = bytes(url, encoding='utf8')
    file_size = 4 + len(url_bytes) + size_mb
    with open(filename, 'wb') as f:
        # 2个字节保存url字节数组的长度
        f.write(len(url_bytes).to_bytes(2, 'big'))
        # 写入url字节数组
        f.write(url_bytes)
        # 2个字节保存文件的size(unit: MB)
        f.write(size_mb.to_bytes(2, 'big'))

        f.seek(file_size - 1)
        f.write(b'\x00')
    return 0, [0] * size_mb, file_size - size_mb


def read_odl_file(filename):
    pieces = []
    cnt_p = 0
    with open(filename, 'rb') as f:
        data = f.read()
        url_b_len = int.from_bytes(data[:2], 'big')
        url = str(data[2: 2 + url_b_len], encoding='utf8')
        offset = url_b_len + 4
        size_mb = int.from_bytes(data[offset - 2:offset], 'big')
        for i in range(offset, offset + size_mb):
            if data[i] == 0:
                pieces.append(0)
            else:
                pieces.append(1)
                cnt_p += 1
    return cnt_p, pieces, offset, url
