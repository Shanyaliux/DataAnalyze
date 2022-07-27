import argparse
import os
import json
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

from utils.read import readCoco, readVoc


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
        self.eachImageCategoryNum = {}
        self.eachImageBboxNum_list = []
        self.sizeBboxNum = dict.fromkeys(['small', 'medium', 'large'], 0)

        if not os.path.exists(self.outPath):
            os.makedirs(self.outPath)

        print('Processing, please wait...')

        if type == 'coco':
            self.analyzeInfo(readCoco(path))
            self.drawAll()
        elif type == 'voc':
            self.analyzeInfo(readVoc(path))
            self.drawAll()
        else:
            print('Currently only voc and coco formats are supported, please check if the first parameter is correct.')
        
        print(f'Processing completed. The result is saved in {self.outPath}.')

    def analyzeInfo(self, info_data):
        
        self.imagesNum = len(info_data)
        for info in info_data:
            w, h = info['width'], info['height']
            self.imageWH_list[0].append(float(w))
            self.imageWH_list[1].append(float(h))
            calculatedCategory = []
            for obj in info['bndbox']:
                w = float(obj['xmax']) - float(obj['xmin'])
                h = float(obj['ymax']) - float(obj['ymin'])
                self.bboxWH_list[0].append(w)
                self.bboxWH_list[1].append(h)
                try:
                    self.anchorRatio_list.append(self.calculateAnchorRatio(w, h))
                except Exception:
                    self._extracted_from_analyzeInfo_17()
                    print(info['file'], 'Image has wrong height and width.')
                    self._extracted_from_analyzeInfo_17()
                self.allCategories.append(obj['objName'])
                if obj['objName'] not in self.eachCategoryBboxWH.keys():
                    self.eachCategoryBboxWH.update({obj['objName']: [[w], [h]]})
                else:
                    self.eachCategoryBboxWH[obj['objName']][0].append(w)
                    self.eachCategoryBboxWH[obj['objName']][1].append(h)
                if obj['objName'] not in self.eachCategoryImageNum.keys():
                    self.eachCategoryImageNum.update({obj['objName']: 1})
                    calculatedCategory.append(obj['objName'])
                elif obj['objName'] not in calculatedCategory:
                    self.eachCategoryImageNum[obj['objName']] += 1
                    calculatedCategory.append(obj['objName'])
            if len(calculatedCategory) not in self.eachImageCategoryNum.keys():
                self.eachImageCategoryNum.update({len(calculatedCategory): 1})
            else:
                self.eachImageCategoryNum[len(calculatedCategory)] += 1
            self.eachImageBboxNum_list.append(len(info['bndbox']) - 2)
        self.bboxNum = len(self.anchorRatio_list)
        area_list = np.multiply(np.array(self.bboxWH_list[0]), np.array(self.bboxWH_list[1]))
        for area in area_list:
            if area < (32 * 32):
                self.sizeBboxNum['small'] += 1
            elif area < (96 * 96):
                self.sizeBboxNum['medium'] += 1
            else:
                self.sizeBboxNum['large'] += 1

    # TODO Rename this here and in `analyzeInfo`
    def _extracted_from_analyzeInfo_17(self):
        print()
        print('============ Errors ============')
        print()

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
        r_dict = {item: self.anchorRatio_list.count(item) for item in set(self.anchorRatio_list)}

        self.drawBar(r_dict.keys(), r_dict.values(),
                     'AnchorBoxRatioBar', 'ratio', 'num', 'AnchorBoxRatio.png')

    def drawEachCategoryNum(self):
        c_dict = {item: self.allCategories.count(item) for item in set(self.allCategories)}

        self.drawBar(c_dict.keys(), c_dict.values(),
                     'the numbers of category', 'category', 'num', 'EachCategoryNum.png')
        size = {key: c_dict[key] / len(self.allCategories) for key in c_dict}
        self.drawPie(size.values(), size.keys(), 'the numbers of category', 'EachCategoryNumPie.png')

    def drawEachCategoryImagesNum(self):
        self.drawBar(self.eachCategoryImageNum.keys(), self.eachCategoryImageNum.values(),
                     'the numbers of images for each category', 'category', 'num', 'EachCategoryImagesNum.png')

    def drawEachImageBboxNum(self):
        c_dict = {item: self.eachImageBboxNum_list.count(item) for item in set(self.eachImageBboxNum_list)}

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
            self.drawScatter(self.eachCategoryBboxWH[c][0], self.eachCategoryBboxWH[c][1], f'{c}WH', 'w', 'h', os.path.join('EachCategoryBboxWH', f'{c}WH.png'))

    def drawAll(self):
        self._extracted_from_drawAll_2()
        print('number of images: %d' % self.imagesNum)
        print('number of boxes: %d' % len(self.anchorRatio_list))
        className_list = set(self.allCategories)
        print('classes = ', list(className_list))
        self._extracted_from_drawAll_2()
        self.drawEachCategoryBboxWH()
        self.drawImageWHScatter()
        self.drawBboxWHScatter()
        self.drawSizeBboxNum()
        self.drawAnchorRatioBar()
        self.drawEachCategoryImagesNum()
        self.drawEachCategoryNum()
        self.drawEachImageBboxNum()

    # TODO Rename this here and in `drawAll`
    def _extracted_from_drawAll_2(self):
        print()
        print('***************** Info *****************')
        print()

    def calculateAnchorRatio(self, w, h):
        """
        calculate anchor ratio
        :param w: width
        :param h: height
        :return: AnchorRatio
        """
        r = w / h if w > h else h / w
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
        self._extracted_from_drawBar_4(title, xlabel, ylabel, imgName)

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
        self._extracted_from_drawBar_4(title, xlabel, ylabel, imgName)

    # TODO Rename this here and in `drawScatter` and `drawBar`
    def _extracted_from_drawBar_4(self, title, xlabel, ylabel, imgName):
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
    parser.add_argument('type', type=str, help="Dataset format, optional 'voc' and 'coco'")
    parser.add_argument('path', type=str, help='Dataset path, if it is a voc dataset, it corresponds '
                                               'to the xml directory, if it is a coco dataset, it is the json file '
                                               'path')
    parser.add_argument('--out', type=str, default='out', help='Result output directory')
    return parser.parse_args()


def main():
    args = parse_args()
    DataAnalyze(args.type, args.path, args.out)


if __name__ == '__main__':
    main()
