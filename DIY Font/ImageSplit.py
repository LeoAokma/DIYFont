from PIL import Image
import os
import cv2
import imutils
from imutils.perspective import four_point_transform


def cut_edge(img_file):
    image = cv2.imread(img_file, 1)
    # 自适应二值化方法
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    cv2.imshow('', edged)
    cv2.waitKey(1000)
    # 从边缘图中寻找轮廓，然后初始化答题卡对应的轮廓
    cnts, hirerachy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    docCnt = None
    # 确保至少有一个轮廓被找到
    if len(cnts) > 0:
        # 将轮廓按大小降序排序
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        # 对排序后的轮廓循环处理
        for c in cnts:
            # 获取近似的轮廓
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            # 如果近似轮廓有四个顶点，那么就认为找到了答题卡
            if len(approx) == 4:
                docCnt = approx
                break
    paper = four_point_transform(image, docCnt.reshape(4, 2))
    cv2.imwrite(img_file, paper)


file_dir = input('请输入存放扫描得到的图片文件所在的文件夹：\n[提示]必须用正斜杠表示路径"/"而不是反斜杠"\\"\n').strip()
if file_dir[-1] != '/':
    file_dir += '/'
files = os.listdir(file_dir)
file_list = []
for _ in files:
    file_list.append(file_dir + _)
files = file_list

is_cut = input('是否对扫面图片进行裁剪：（Y/N）？\n[提示]该步骤将字体表格周围的空白全部去除，并且尝试将方格对其水平\n')
if is_cut.lower() == 'y':
    for _ in files:
        cut_edge(_)
    print('图片边框识别完成，切割和对齐完成！')

label_file = 'D:/Mydata/Photoshop/G2312/GB2312_text.txt'
safe_file = input('请输入存放切割后单字图片的文件夹路径\n[提示]仅输入文件夹路径，需要先创建好文件夹！\n同样需要用正斜杠'
                  '"/"分割文件路径，和前面相同！\n[提示]文件数量比较多，请新建一个文件夹并且放入\n').strip()
if safe_file[-1] != '/':
    safe_file += '/'
with open(label_file) as f:
    labels = f.readlines()

for _ in labels:
    _ = _.strip()

H = 268.69
W = 179
w_0 = 11.6
h_0 = 0
dw = 22.4
dh = 11.2
w = 10.45
h = 10.9


for img_file in files:
    i = 1
    number = int(img_file.split('/')[-1].split('.')[0])
    img = Image.open(img_file)
    img_size = img.size
    a = img_size[0] #图片宽度
    b = img_size[1] #图片高度
    for y in range(24):
        for x in range(8):
            index = (number - 1) * 8 * 24 + i
            img.crop(((w_0 + x*dw + 0.1)*a/W, (h_0 + y*dh + 0.1)*b/H, (w_0 + x*dw + w)*a/W, (h_0 + y*dh + h)*b/H)).\
                save(safe_file + "{}.jpg".format(labels[index].strip()))
            i += 1

print('图片分割完成！请检查图片是否正常，如果不正常请重新扫描出错的图片')
