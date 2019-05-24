# OneDrive video downloader

个人使用OneDrive搭了一个网盘，想在线看视频，但是网速总是不稳定。由于OneDrive可以支持多个连接，（具体最大有多少不清楚）于是采用多线程下载的方法实现视频的边下边播。

## 原理

我是用的多线程并不是平均分成多少段，而是把视频分割成单位为1M的片段。按顺序将这些片段放到队列里，然后多线程消耗，以此达到顺序播放不卡顿的效果。（有些视频格式的索引表在结尾，所以首先下载尾部20M）

## 环境

- `python3`
- `requests>=2.22.0`

## 用法

    $ python app.py -h
    usage: app.py [-h] [-d dir] [-n num] [-c ovd_file] [--set-d dir] [--set-n num]
                  [url [url ...]]

    positional arguments:
      url          download url

    optional arguments:
      -h, --help   show this help message and exit
      -d dir       save directory
      -n num       number of thread
      -c ovd_file  continue to download (TODO) //暂未完成

    settings arguments:
      --set-d dir  set the save directory (default: .)
      --set-n num  set the thread number (default: 8, max: 32)

如果同时设置`-d`和`--set-d`参数，会将视频保存到`-d`参数的值，`--set-d`的值下次执行命令的时候生效

设置类的参数可以不带`url`，例如

    python app.py --set-d d:/movies --set-n 32
