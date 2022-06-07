# TimePhoto
时光相册照片批量下载脚本

## Install
    - 下载源文件

## Structure
    - cache: 存储下载中需要的 URL / meidatoken 等变量
    - data: 文件下载路径
    - download：多线程 download.py 下载文件夹
    - download.py: 多线程文件分块下载实现
    - multiprocessing.py: 多进程 时光相册 照片下载实现
    - simpleSpider.py: 单线程 时光相册 照片下载实现

## Usage
    - 修改 multiprocessing.py 105行 的cookie。
    - 在 python 3.9.2 环境下运行脚本

## Todo
    - 文件分块多线程下载
    - 按照相册类别下载
    - Gui

## Maintainer
[![Shem Todo](https://img.shields.io/badge/Shem-blue.svg)](https://github.com/Sakura-shem)

## License
[MIT](https://github.com/RichardLitt/standard-readme/blob/master/LICENSE) © Shem
