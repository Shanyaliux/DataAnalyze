### Install

```bash
git clone https://github.com/Shanyaliux/DataAnalyze.git
cd DataAnalyze
pip install -r requirements.txt
```

### Usage

```bash
python DataAnalyze.py ${type} ${path} [--out ${out}]
```
- `type` The format of the dataset, optional 'coco' or 'voc'. 
- `path` The path of dataset.
If `type` is 'coco', the `path` is the json file path. 
If `type` is 'voc', the `path` is the path of the xml file directory.  
- `--out` is the output directory, default is './out'

#### Example
```bash
python DataAnalyze.py coco ./tarin.json --out ./out/
```

```bash
python DataAnalyze.py voc ./xml/ --out ./out/
```

![](./sample/boxWH.png)
![](./sample/AnchorBoxRatio.png)
![](./sample/EachClassNum.png)
![](./sample/EachClassNumPie.png)


