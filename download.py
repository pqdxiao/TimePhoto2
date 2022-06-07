from multiprocessing import Pool
import time, requests, os, threading

def split(end: int, step: int) -> list[tuple[int, int]]:
    # 分多块
    parts = [(start, min(start + step, end)) for start in range(0, end, step)]
    return parts

def download(list):

    def start_download(list):
        num, start, end, url, stamp = list
        print('进程{}， 开始下载第{}块'.format(stamp, num))
        f = open(f'./download/cache/{stamp}{num}', 'wb')
        _headers = headers.copy()
        # 分段下载的核心
        _headers['Range'] = f'bytes={start}-{end}'
        # 发起请求并获取响应（流式）
        response = session.get(url, headers = _headers, stream=True)
        # 每次读取的流式响应大小
        chunk_size = 128
        # 暂存已获取的响应，后续循环写入
        chunks = []
        for chunk in response.iter_content(chunk_size = chunk_size):
            # 暂存获取的响应
            chunks.append(chunk)
        for chunk in chunks:
            f.write(chunk)
        # 释放已写入的资源
        del chunks
        f.close()
        print('进程{}， 第{}块下载结束'.format(stamp, num))

    url, stamp = list
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    session = requests.Session()
    res = requests.get(url, headers = headers, stream = True)
    file_size = int(res.headers['Content-Length'])  # 141062
    # 分块文件如果比文件大，就取文件大小为分块大小
    each_size = min(int(file_size / 5), file_size)
    parts = [(start, min(start + each_size, file_size)) for start in range(0, file_size, each_size)]
    num = 0
    task = []
    for part in parts:
        start, end = part
        # 开启多线程
        task.append( threading.Thread(target = start_download, args = ([num, start, end, url, stamp],)) )
        num += 1
        task[-1].start()

    while True:
        live = len(task)
        print(f"{stamp}检测线程")
        for i in range(len(task)):
            if not task[i].is_alive():
                live -= 1
        time.sleep(1)
        if not live:
            print(f"{stamp}下载结束")
            # 文件合并
            file = open(f"download/cache/{stamp}", 'wb')
            for i in range(num):
                url = f'./download/cache/{stamp}{i}'
                with open(url, 'rb') as f:
                    data = f.read(1024)
                    while data:
                        file.write(data)
                        data = f.read(1024)
                os.remove(url)
            file.close()
            print("{stamp} 文件合并完成")
            break



if __name__ == "__main__":
    url = 'https://media.everphoto.cn/archive/download?archivetoken=97JBVbXaLE4_2fAFzrUyDPxV'
    pool = Pool(processes = 2)
    for i in range(2):
        pool.apply_async(download, args=([url, i],))
    pool.close()
    pool.join()

