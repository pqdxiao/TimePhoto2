import requests, pickle, os, threading, time
from multiprocessing import Pool, Queue


class TimePhoto():
    def __init__(self, cookie):
        self.username = ""
        self.password = ""
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            "referer": "https://web.everphoto.cn/",
            "cookie":cookie,
            }
        self.UrlList = self.MediaList = []
        self.MediaQueue = Queue()
        self.UrlQueue = Queue()
        self.size = self.UrlQueue.qsize()
        self.Flag = self.initialization()

    def initialization(self):
        if os.path.exists("./cache/UrlList.pkl"):
            self.UrlList, self.UrlQueue = self.load_data("UrlList")
            print("UrlList loaded", len(self.UrlList))
            return 1
        else:
            if os.path.exists("./cache/mediaList.pkl"):
                self.MediaList, self.MediaQueue = self.load_data("MediaList")
                print("load MediaList from cache")
            else:
                self.MediaList = self.get_MediaList()
                self.save_data("MediaList", self.MediaList)
                for i in self.MediaList:
                    self.MediaQueue.put(i)
            return 0

    def load_data(self, url):
        with open("./cache/{0}.pkl".format(url), "rb") as f:
            List = pickle.load(f)
        queue = Queue()
        for i in List:
            queue.put(i)
        return List, queue

    def save_data(self, url, List):
        with open("./cache/{0}.pkl".format(url), "wb") as f:
            pickle.dump(List, f)

    def get_MediaList(self):
        
        def get(session, headers, prev = None):
            url = "https://web.everphoto.cn/api/users/self/updates?count=200"
            if prev:
                url = "https://web.everphoto.cn/api/users/self/updates?count=200&p={0}".format(prev)

            res = session.get(url, headers = headers).json()
            return res
        res = get(self.session, self.headers)
        MediaList = []
        MediaOrientation = []
        while True:
            try:
                MediaList.append([i["id"] for i in res["data"]["media_list"]])
                MediaOrientation.append([i["orientation"] for i in res["data"]["media_list"]])
                prev = res["pagination"]["prev"]
            except:
                break
            res = get(self.session, self.headers, prev)
        temp = []
        for i in MediaList:
            temp.append("")
            for j in i:
                temp[-1] = temp[-1] + "-" +str(j)
            temp[-1] = temp[-1][1::]
        MediaList = temp
        return MediaList

def download(list):
    url, num, headers = list
    print("downloading {0}".format(url))
    session = requests.session()
    res = session.get(url, headers = headers)
    file = res.content
    if not os.path.exists("./data"):
        os.mkdir("./data")
    with open(os.path.join("./data", '{0}.zip'.format(num)), 'wb') as f:
        f.write(file)
    return 1

def get_downloadurl(list):
    media, headers = list
    url = "https://web.everphoto.cn/api/media/archive"
    data = {"media":media}
    session = requests.session()
    res = session.post(url, headers = headers, data = data).json()
    try:
        UrlQueue.put(res['data']['url'])
        print(UrlQueue.qsize())
        return [res['data']['url'], UrlQueue.qsize()]
    except Exception as e:
        print("error")
        return [0, 0]

if __name__ == "__main__":
    cookie = ""
    timePhoto = TimePhoto(cookie)
    if not timePhoto.Flag:
        task = []
        UrlQueue = Queue()
        for i in timePhoto.MediaList:
            task.append(threading.Thread(target = get_downloadurl, args = ([i, timePhoto.headers],)))
            task[-1].start()
        while True:
            live = len(task)
            for i in range(len(task)):
                if not task[i].is_alive():
                    live -= 1
            time.sleep(1)
            if not live:
                print("UrlQueue size:", UrlQueue.qsize())
                while not UrlQueue.empty():
                    timePhoto.UrlList.append(UrlQueue.get())
                timePhoto.save_data("UrlList", timePhoto.UrlList)
                break
    pool = Pool(processes = 5)
    print("start download")
    for i, j in zip(timePhoto.UrlList, range(len(timePhoto.UrlList))):
        pool.apply_async(download, args = ([i, j, timePhoto.headers],))
    pool.close() 
    pool.join()