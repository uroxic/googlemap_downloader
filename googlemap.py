import requests
import threading
import math
import os
from PIL import Image

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/63.0.3239.132 Safari/537.36'}


class downloadThread (threading.Thread):
    def __init__(self, idd, s, e, xmin, ymin, xmax, ymax, num):
        threading.Thread.__init__(self)
        self.id = idd
        self.s = s
        self.e = e
        self.xmin = min(xmin,xmax)
        self.ymin = min(ymin,ymax)
        self.xmax = max(xmin,xmax)
        self.ymax = max(ymin,ymax)
        self.num = num

    def run(self):
        for i in range(self.s, self.e):
            savepath = "./" + str(i) + "/"
            try:
                if (os.path.exists(savepath) == 0):
                    os.makedirs(savepath)
            except:
                pass
            if ((int(pow(2, i) * self.ymax) - int(pow(2, i) * self.ymin)) <= self.num and self.id < (int(pow(2, i) * self.ymax) - int(pow(2, i) * self.ymin))):
                ss = self.id + int(pow(2, i) * self.ymin)
                ee = ss + 1
            elif ((int(pow(2, i) * self.ymax) - int(pow(2, i) * self.ymin)) > self.num):
                ss = (self.id * (int(pow(2, i) * self.ymax) - int(pow(2, i)
                      * self.ymin))) // self.num + int(pow(2, i) * self.ymin)
                ee = ((self.id + 1) * (int(pow(2, i) * self.ymax) - int(pow(2, i)
                      * self.ymin))) // self.num + int(pow(2, i) * self.ymin)
            else:
                ss = ee = 0
            for j in range(ss, ee):
                for k in range(int(pow(2, i) * self.xmin), int(pow(2, i) * self.xmax)):
                    if (os.path.exists(savepath + str(k) + "_" + str(j) + ".jpg")):
                        continue
                    url = "https://mts0.googleapis.com/vt?lyrs=s&x=" + \
                        str(k) + "&y=" + str(j) + "&z=" + str(i)
                    trynum = 0
                    while(trynum < 3):
                        trynum += 1
                        try:
                            pic = requests.get(url, headers=header)
                            if pic.status_code == 200:
                                filename = str(k) + "_" + str(j) + ".jpg"
                                with open(os.path.join(savepath)+filename, 'wb') as fp:
                                    fp.write(pic.content)
                                    fp.close()
                            print(filename + "_下载完成")
                            break
                        except:
                            print(str(k) + "_" + str(j) + "_获取失败")


s = 0
e = 0
minlng = 0.0
minlat = 0.0
maxlng = 0.0
maxlat = 0.0
s = int(input())
e = int(input())
minlat = float(input())
minlng = float(input())
maxlat = float(input())
maxlng = float(input())
threadnum = 96
xmin = ((minlng + 180.0) / 360.0)  # 除以2指数后的xmin,下同,即此参数需乘以2指数后可用
ymin = ((math.pi - math.asinh(math.tan(minlat * math.pi / 180)))/(2 * math.pi))
xmax = ((maxlng + 180.0) / 360.0)
ymax = ((math.pi - math.asinh(math.tan(maxlat * math.pi / 180)))/(2 * math.pi))
threadlist = []
for i in range(threadnum):
    threadlist.append(downloadThread(
        i, s, e, xmin, ymin, xmax, ymax, threadnum))
    threadlist[i].start()

for i in threadlist:
    i.join()

for i in range(s, e):
    dest_im = Image.new('RGBA', ((int(pow(2, i) * xmax) - int(pow(2, i) * xmin)) *
                        256, (int(pow(2, i) * ymax) - int(pow(2, i) * ymin)) * 256), (255, 255, 255))
    dest_im.save(str(i) + ".png", 'png')
    for j in range(int(pow(2, i) * ymax) - int(pow(2, i) * ymin)):
        for k in range(int(pow(2, i) * xmax) - int(pow(2, i) * xmin)):
            savepath = "./" + str(i) + "/"
            filename = str(k + int(pow(2, i) * xmin)) + "_" + str(j + int(pow(2, i) * ymin)) + ".jpg"
            src_im = Image.open(savepath+filename)
            dest_im.paste(src_im, (k * 256, j * 256))
    dest_im.save(str(i) + ".png", 'png')
