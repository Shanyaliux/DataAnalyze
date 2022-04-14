import argparse
import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


class DataAnalyze:
    def __init__(self, xmlPath, outPath):
        self.xmlPath = xmlPath
        self.outPath = outPath
        if not os.path.exists(self.outPath):
            os.makedirs(self.outPath)
        self.vocInfo = self.readVoc()
        self.statisticsInfo()

    def statisticsInfo(self):
        lines = self.vocInfo.strip('\n').split('\n')
        print('number of images: %d' % len(lines))
        imgWH_list = [[], []]
        boxWH_list = [[], []]
        anchorRatio_list = []
        eachClass_list = []
        eachImageObject_list = []
        for i, line in enumerate(lines):
            lin = line.strip(' ').split(' ')
            h, w = lin[1].split(',')
            imgWH_list[0].append(int(w))
            imgWH_list[1].append(int(h))
            for obj in lin[2:]:
                ob = obj.split(',')
                w = int(ob[2]) - int(ob[0])
                h = int(ob[3]) - int(ob[1])
                boxWH_list[0].append(w)
                boxWH_list[1].append(h)
                anchorRatio_list.append(self.computeAnchorRatio(w, h))
                eachClass_list.append(ob[-1])
            eachImageObject_list.append(len(lin) - 2)
        print('number of boxes: %d' % len(anchorRatio_list))
        self.drawScatter(imgWH_list[0], imgWH_list[1], 'Image w h', 'w', 'h', 'WH.png')
        self.drawScatter(boxWH_list[0], boxWH_list[1], 'box w h', 'w', 'h', 'boxWH.png')
        self.statisticsAnchorRatio(anchorRatio_list)
        self.statisticsEachClassNum(eachClass_list)
        self.statisticsEachImageObjectNum(eachImageObject_list)
        className_list = set(eachClass_list)
        print('classes = ', list(className_list))
        self.statisticsEachClassObjectWH(className_list)

    @staticmethod
    def readXml(xml, ignoreDiff=False):
        root = ET.parse(xml).getroot()
        filename = root.find('filename').text
        size = root.find('size')
        width = size.find('width').text
        height = size.find('height').text
        xmlInfo = "%s %s,%s " % (filename, width, height)
        for obj in root.findall('object'):
            if ignoreDiff:
                if obj.find('difficult') is not None:
                    difficult = obj.find('difficult').text
                    if int(difficult) == 1:
                        continue
            obj_name = obj.find('name').text
            bndbox = obj.find('bndbox')
            left = bndbox.find('xmin').text
            top = bndbox.find('ymin').text
            right = bndbox.find('xmax').text
            bottom = bndbox.find('ymax').text
            xmlInfo += "%s,%s,%s,%s,%s " % (left, top, right, bottom, obj_name)
        xmlInfo += '\n'
        return xmlInfo

    def readVoc(self):
        vocInfo = ''
        xmlList = os.listdir(self.xmlPath)
        xmlList.sort()
        for xml in xmlList:
            xmlFile = os.path.join(self.xmlPath, xml)
            vocInfo += self.readXml(xmlFile)
        return vocInfo

    @staticmethod
    def computeAnchorRatio(w, h):
        if w > h:
            r = w / h
        else:
            r = h / w
        return round(r)

    def statisticsAnchorRatio(self, anchorRatio_list):
        r_dict = {}
        for item in set(anchorRatio_list):
            r_dict.update({item: anchorRatio_list.count(item)})
        self.drawBar(r_dict.keys(), r_dict.values(),
                     'AnchorBoxRatio', 'ratio', 'num', 'AnchorBoxRatio.png')

    def statisticsEachClassNum(self, eachClass_list):
        c_dict = {}
        for item in set(eachClass_list):
            c_dict.update({item: eachClass_list.count(item)})
        self.drawBar(c_dict.keys(), c_dict.values(),
                     'EachClassNum', 'class', 'num', 'EachClassNum.png')

        size = {}
        for key in c_dict:
            size.update({key: c_dict[key] / len(eachClass_list)})
        self.drawPie(size.values(), size.keys(), 'EachClassNum', 'EachClassNumPie.png')

    def statisticsEachImageObjectNum(self, eachImageObject_list):
        eion_dict = {}
        for item in set(eachImageObject_list):
            eion_dict.update({item: eachImageObject_list.count(item)})
        self.drawBar(eion_dict.keys(), eion_dict.values(),
                     'Number of boxes on each image', 'boxNum', 'imageNum', 'EachImageBoxes.png')

    def statisticsEachClassObjectWH(self, className_list):
        lines = self.vocInfo.strip('\n').split('\n')
        if not os.path.exists(os.path.join(self.outPath, 'EachClassBoxWH')):
            os.makedirs(os.path.join(self.outPath, 'EachClassBoxWH'))
        ecoWH_dict = {}
        for cn in className_list:
            ecoWH_dict.update({cn: [[], []]})
        for line in lines:
            lin = line.strip(' ').split(' ')
            for obj in lin[2:]:
                ob = obj.split(',')
                w = int(ob[2]) - int(ob[0])
                h = int(ob[3]) - int(ob[1])
                ecoWH_dict[ob[-1]][0].append(w)
                ecoWH_dict[ob[-1]][1].append(h)
        for c in ecoWH_dict:
            self.drawScatter(ecoWH_dict[c][0], ecoWH_dict[c][1],
                             c + 'WH', 'w', 'h', os.path.join('EachClassBoxWH', c + 'WH.png'))

    def drawScatter(self, x, y, title, xlabel, ylabel, imgName):
        plt.scatter(x, y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.savefig(os.path.join(self.outPath, imgName))
        plt.close()

    def drawBar(self, x, y, title, xlabel, ylabel, imgName):
        rects = plt.bar(x, y)
        for rect in rects:  # rects 是柱子的集合
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2, height, str(height), ha='center', va='bottom')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.savefig(os.path.join(self.outPath, imgName))
        plt.close()

    def drawPie(self, size, labels, title, imgName):
        plt.pie(size, labels=labels, labeldistance=1.1,
                autopct="%1.1f%%", shadow=False, startangle=90, pctdistance=0.6)
        plt.title(title)
        plt.axis("equal")  # 设置横轴和纵轴大小相等，这样饼才是圆的
        plt.savefig(os.path.join(self.outPath, imgName))
        plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description='dataset analyze')
    parser.add_argument('xmlPath', type=str, help='xml file')
    parser.add_argument('--outPath', type=str, help='out file', default='out')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    DataAnalyze(args.xmlPath, args.outPath)


if __name__ == '__main__':
    main()
