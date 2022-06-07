import requests, struct, pickle, os


class TimePhoto():
    def __init__(self) -> None:
        self.username = ""
        self.password = ""
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            "referer": "https://web.everphoto.cn/",
            "cookie":"access_token=gxKCvery6XSYiXAKkKfbH5hV",
            }

    # get all media token
    def get_mediatoken(self, prev = None):
        url = "https://web.everphoto.cn/api/users/self/updates?count=200"
        if prev:
            url = "https://web.everphoto.cn/api/users/self/updates?count=200&p={0}".format(prev)

        res = self.session.get(url, headers=self.headers).json()
        return res

    def get_downloadurl(self, media):
        url = "https://web.everphoto.cn/api/media/archive"
        data = {"media":media}
        res = self.session.post(url, headers = self.headers, data = data).json()
        try:
            print("666")
            return res['data']['url']
        except:
            print(res)
            return None 

    def judge_file(self, file):
        type_dict = {
            '424D': 'bmp',
            'FFD8FF': 'jpg',
            '2E524D46': 'rm',
            '4D546864': 'mid',
            '89504E47': 'png',
            '47494638': 'gif',
            '49492A00': 'tif',
            '41433130': 'dwg',
            '38425053': 'psd',
            '2142444E': 'pst',
            'FF575043': 'wpd',
            'AC9EBD8F': 'qdf',
            'E3828596': 'pwl',
            '504B0304': 'zip',
            '52617221': 'rar',
            '57415645': 'wav',
            '41564920': 'avi',
            '2E7261FD': 'ram',
            '000001BA': 'mpg',
            '000001B3': 'mpg',
            '6D6F6F76': 'mov',
            '7B5C727466': 'rtf',
            '3C3F786D6C': 'xml',
            '68746D6C3E': 'html',
            'D0CF11E0': 'doc/xls',
            '255044462D312E': 'pdf',
            'CFAD12FEC5FD746F': 'dbx',
            '3026B2758E66CF11': 'asf',
            '5374616E64617264204A': 'mdb',
            '252150532D41646F6265': 'ps/eps',
            '44656C69766572792D646174653A': 'eml'
        }
        max_len = len(max(type_dict, key=len)) // 2
        # 读取二进制文件开头一定的长度
        byte = file[0:max_len:1]
        # 解析为元组
        byte_list = struct.unpack('B' * max_len, byte)
        # 转为16进制
        code = ''.join([('%X' % each).zfill(2) for each in byte_list])
        # 根据标识符筛选判断文件格式
        result = list(filter(lambda x: code.startswith(x), type_dict))
        
        if result:
            return type_dict[result[0]]
        else:
            return None

if __name__ == "__main__":
    timePhoto = TimePhoto()
    res = timePhoto.get_mediatoken()
    mediaList = []
    while True:
        try:
            mediaList.append([i["id"] for i in res["data"]["media_list"]])
            prev = res["pagination"]["prev"]
        except:
            break
        res = timePhoto.get_mediatoken(prev)
    temp0 = []
    for i in mediaList:
        temp = ""
        for j in i:
            temp = temp + "-" +str(j)
        temp0.append(temp[1::1])
    mediaList = temp0

    mediaList = [y for x in mediaList for y in x]
    with open('./cache/mediaList.pkl', 'rb') as f:
        mediaList = pickle.load(f)
    url = []
    for i in mediaList:
        if timePhoto.get_downloadurl(i):
            url.append(timePhoto.get_downloadurl(i))
            print(len(url))
    with open("url.pkl", "wb") as f:
        pickle.dump(url, f)
    
    # 5043
    with open("url.pkl", "rb") as f:
        url = pickle.load(f)
    print(len(url))
    num = 0
    for i in url:
        res = timePhoto.session.get(i, headers=timePhoto.headers)
        img = res.content
        filetype = timePhoto.judge_file(img)
        print(filetype)
        if filetype:
            if not os.path.exists(filetype):
                os.mkdir(filetype)
            with open( './{1}/{0}.{1}'.format(num, filetype), 'wb') as f:
                f.write(img)
            num += 1

