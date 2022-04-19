import argparse
import os
import json
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np


class DataAnalyze:
    """
    voc or coco dataset analyze
    """
    def __init__(self, type, path, outPath):
        """
        :param type: dataset format, optional: 'coco', 'voc'
        :param path: dataset path
        :param outPath: result path
        """
        self.outPath = outPath

        self.imageWH_list = [[], []]
        self.bboxWH_list = [[], []]
        self.anchorRatio_list = []
        self.imagesNum = 0
        self.bboxNum = 0
        self.allCategories = []
        self.eachCategoryBboxWH = {}
        self.eachCategoryImageNum = {}
        # self.eachCategoryBboxNum = {}
        self.eachImageCategoryNum = {}
        self.eachImageBboxNum_list = []
        self.sizeBboxNum = dict.fromkeys(['small', 'medium', 'large'], 0)

        if not os.path.exists(self.outPath):
            os.makedirs(self.outPath)
        if type == 'coco':
            # self.statisticsInfo(self.readCoco(path))
            self.analyzeInfo(self.readCoco(path))
            self.drawAll()
        elif type == 'voc':
            # self.statisticsInfo(self.readVoc(path))
            self.analyzeInfo(self.readVoc(path))
            self.drawAll()
        else:
            print('Currently only voc and coco formats are supported, please check if the first parameter is correct.')

    def analyzeInfo(self, info_data):
        lines = info_data.strip('\n').split('\n')
        self.imagesNum = len(lines)
        for i, line in enumerate(lines):
            lin = line.strip(' ').split(' ')
            w, h = lin[1].split(',')
            self.imageWH_list[0].append(float(w))
            self.imageWH_list[1].append(float(h))
            calculatedCategory = []
            for obj in lin[2:]:
                ob = obj.split(',')
                w = float(ob[2]) - float(ob[0])
                h = float(ob[3]) - float(ob[1])
                self.bboxWH_list[0].append(w)
                self.bboxWH_list[1].append(h)
                self.anchorRatio_list.append(self.calculateAnchorRatio(w, h))
                self.allCategories.append(ob[-1])
                # if ob[-1] not in self.eachCategoryBboxNum.keys():
                #     self.eachCategoryBboxNum.update({ob[-1]: 1})
                # else:
                #     self.eachCategoryBboxNum[ob[-1]] += 1
                if ob[-1] not in self.eachCategoryBboxWH.keys():
                    self.eachCategoryBboxWH.update({ob[-1]: [[w], [h]]})
                else:
                    self.eachCategoryBboxWH[ob[-1]][0].append(w)
                    self.eachCategoryBboxWH[ob[-1]][1].append(h)
                if ob[-1] not in self.eachCategoryImageNum.keys():
                    self.eachCategoryImageNum.update({ob[-1]: 1})
                    calculatedCategory.append(ob[-1])
                else:
                    if ob[-1] not in calculatedCategory:
                        self.eachCategoryImageNum[ob[-1]] += 1
                        calculatedCategory.append(ob[-1])
            if len(calculatedCategory) not in self.eachImageCategoryNum.keys():
                self.eachImageCategoryNum.update({len(calculatedCategory): 1})
            else:
                self.eachImageCategoryNum[len(calculatedCategory)] += 1
            self.eachImageBboxNum_list.append(len(lin) - 2)
        self.bboxNum = len(self.anchorRatio_list)
        area_list = np.multiply(np.array(self.bboxWH_list[0]), np.array(self.bboxWH_list[1]))
        for area in area_list:
            if area < (32 * 32):
                self.sizeBboxNum['small'] += 1
            elif area < (96 * 96):
                self.sizeBboxNum['medium'] += 1
            else:
                self.sizeBboxNum['large'] += 1

    def drawImageWHScatter(self):
        self.drawScatter(self.imageWH_list[0],
                         self.imageWH_list[1],
                         "Scatter of image W & H",
                         'W', 'H',
                         'imageWH.png')

    def drawBboxWHScatter(self):
        self.drawScatter(self.bboxWH_list[0],
                         self.bboxWH_list[1],
                         "Scatter of bbox W & H",
                         'W', 'H',
                         'bboxWH.png')

    def drawAnchorRatioBar(self):
        r_dict = {}
        for item in set(self.anchorRatio_list):
            r_dict.update({item: self.anchorRatio_list.count(item)})
        self.drawBar(r_dict.keys(), r_dict.values(),
                     'AnchorBoxRatioBar', 'ratio', 'num', 'AnchorBoxRatio.png')

    def drawEachCategoryNum(self):
        c_dict = {}
        for item in set(self.allCategories):
            c_dict.update({item: self.allCategories.count(item)})
        self.drawBar(c_dict.keys(), c_dict.values(),
                     'the numbers of category', 'category', 'num', 'EachCategoryNum.png')
        size = {}
        for key in c_dict:
            size.update({key: c_dict[key] / len(self.allCategories)})
        self.drawPie(size.values(), size.keys(), 'the numbers of category', 'EachCategoryNumPie.png')

    def drawEachCategoryImagesNum(self):
        self.drawBar(self.eachCategoryImageNum.keys(), self.eachCategoryImageNum.values(),
                     'the numbers of images for each category', 'category', 'num', 'EachCategoryImagesNum.png')

    # def drawEachCategoryBboxNum(self):
    #     self.drawBar(self.eachCategoryBboxNum.keys(), self.eachCategoryBboxNum.values(),
    #                  'the numbers of bboxes for each category', 'category', 'num', 'EachCategoryBboxesNum.png')

    def drawEachImageBboxNum(self):
        c_dict = {}
        for item in set(self.eachImageBboxNum_list):
            c_dict.update({item: self.eachImageBboxNum_list.count(item)})
        self.drawBar(c_dict.keys(), c_dict.values(),
                     'the numbers of bboxes included in each image',
                     'numbers of bboxes in each image', 'num', 'EachImageBboxNum.png')

    def drawSizeBboxNum(self):
        self.drawBar(self.sizeBboxNum.keys(), self.sizeBboxNum.values(),
                     'Number of bbox in different sizes', 'size', 'num', 'SizeBboxNum.png')

    def drawEachCategoryBboxWH(self):
        if not os.path.exists(os.path.join(self.outPath, 'EachCategoryBboxWH')):
            os.makedirs(os.path.join(self.outPath, 'EachCategoryBboxWH'))
        for c in self.eachCategoryBboxWH:
            self.drawScatter(self.eachCategoryBboxWH[c][0], self.eachCategoryBboxWH[c][1],
                             c + 'WH', 'w', 'h', os.path.join('EachCategoryBboxWH', c + 'WH.png'))

    def drawAll(self):
        print('number of images: %d' % self.imagesNum)
        print('number of boxes: %d' % len(self.anchorRatio_list))
        className_list = set(self.allCategories)
        print('classes = ', list(className_list))
        self.drawEachCategoryBboxWH()
        self.drawImageWHScatter()
        self.drawBboxWHScatter()
        self.drawSizeBboxNum()
        self.drawAnchorRatioBar()
        # self.drawEachCategoryBboxNum()
        self.drawEachCategoryImagesNum()
        self.drawEachCategoryNum()
        self.drawEachImageBboxNum()

    def readXml(self, xml, ignoreDiff=False):
        """
        read single xml file
        :param xml: xml file path
        :param ignoreDiff: whether to ignore 'difficult'
        :return: xml info, format: 'fileName width,height xmin,ymin,xmax,ymax,class ... '
        """
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

    def readVoc(self, xmlPath):
        """
        read multiple xml file
        :param xmlPath: path of xml file directory
        :return: all xmlInfo, format: 'xmlInfo1\n xmlInfo2\n ... '
        """
        vocInfo = ''
        xmlList = os.listdir(xmlPath)
        xmlList.sort()
        for xml in xmlList:
            xmlFile = os.path.join(xmlPath, xml)
            vocInfo += self.readXml(xmlFile)
        return vocInfo

    def readCoco(self, jsonFile):
        """
        read coco info from json file
        :param jsonFile: path of json file
        :return: cocoInfo, format: 'cocoInfo1\n cocoInfo2\n ... '
        """
        with open(jsonFile) as f:
            jsonData = json.load(f)
            categories_dict = {}
            for categories in jsonData['categories']:
                categories_dict.update({categories['id']: categories['name']})
            info_dict = {}
            for image in jsonData['images']:
                info_dict.update({image['id']: '%s %s,%s ' % (image['file_name'], image['width'], image['height'])})
            for annotation in jsonData['annotations']:
                xmin = annotation['bbox'][0]
                ymin = annotation['bbox'][1]
                xmax = str(float(xmin) + (float(annotation['bbox'][2])))
                ymax = str(float(ymin) + (float(annotation['bbox'][3])))
                boxInfo = '%s,%s,%s,%s,%s ' % (xmin, ymin, xmax, ymax, categories_dict[annotation['category_id']])
                info_dict[annotation['image_id']] += boxInfo
            coco_info = ''
            for info in info_dict:
                coco_info += info_dict[info]
                coco_info += '\n'
            return coco_info

    def calculateAnchorRatio(self, w, h):
        """
        calculate anchor ratio
        :param w: width
        :param h: height
        :return: AnchorRatio
        """
        if w > h:
            r = w / h
        else:
            r = h / w
        return round(r)

    def drawScatter(self, x, y, title, xlabel, ylabel, imgName):
        """
        draw a scatter
        :param x: x
        :param y: y
        :param title: title of image
        :param xlabel: x label of image
        :param ylabel: y label of image
        :param imgName: name of image
        :return:
        """
        plt.scatter(x, y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.savefig(os.path.join(self.outPath, imgName))
        plt.close()

    def drawBar(self, x, y, title, xlabel, ylabel, imgName):
        """
        draw a bar
        :param x: x
        :param y: y
        :param title: title of image
        :param xlabel: x label of image
        :param ylabel: y label of image
        :param imgName: name of image
        :return:
        """
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
        """
        draw a pie
        :param size: size
        :param labels: labels of image
        :param title: title of image
        :param imgName: name of image
        :return:
        """
        plt.pie(size, labels=labels, labeldistance=1.1,
                autopct="%1.1f%%", shadow=False, startangle=90, pctdistance=0.6)
        plt.title(title)
        plt.axis("equal")  # 设置横轴和纵轴大小相等，这样饼才是圆的
        plt.savefig(os.path.join(self.outPath, imgName))
        plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description='dataset analyze')
    parser.add_argument('type', type=str, help="Dataset format, optional 'voc' and 'coco'", default='voc')
    parser.add_argument('path', type=str, help='Dataset path, if it is a voc dataset, it corresponds '
                                               'to the xml directory, if it is a coco dataset, it is the json file '
                                               'path',
                        default='/home/lgh/code/Voc2Coco/NEU-DET/xml')
    parser.add_argument('--out', type=str, default='out', help='Result output directory')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    DataAnalyze(args.type, args.path, args.out)


if __name__ == '__main__':
    main()
