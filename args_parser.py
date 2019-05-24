import argparse

URL = 'url'
DIR = 'dir'
NUM = 'num'
OVD = 'ovd'
ST_DIR = 'st_dir'
ST_NUM = 'st_num'


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('url', metavar='url', nargs='*', help='download url')
    parser.add_argument('-d', metavar='dir', dest=DIR, action='store', help='save directory')
    parser.add_argument('-n', metavar='num', dest=NUM, action='store', help='number of thread', type=int,
                        choices=range(1, 33))
    parser.add_argument('-c', metavar='ovd_file', dest=OVD, action='store', help='continue to download (TODO)')
    settings = parser.add_argument_group('settings arguments')
    settings.add_argument('--set-d', metavar='dir', dest=ST_DIR, action='store',
                          help='set the save directory (default: .)')
    settings.add_argument('--set-n', metavar='num', dest=ST_NUM, action='store',
                          help='set the thread number (default: 8, max: 32)', type=int, choices=range(1, 33))

    args = parser.parse_args()

    return {
        URL: args.url,
        DIR: args.dir,
        NUM: args.num,
        ST_DIR: args.st_dir,
        ST_NUM: args.st_num,
    }


if __name__ == '__main__':
    print(parse_args())
