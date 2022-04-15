### Install

```bash
pip install -r requirements.txt
```

### Usage

```bash
python DataAnalyze.py ${type} ${path} [--outPath ${out}]
```
- `type` The format of the dataset, optional 'coco' or 'voc'. 
- `path` The path of dataset.
If `type` is 'coco', the `path` is the json file path. 
If `type` is 'voc', the `path` is the path of the xml file directory.  
- `--outPath` is the output directory, default is './out'

#### Example
```bash
python DataAnalyze.py coco ./tarin.json --outPath ./out/
```

```bash
python DataAnalyze.py voc ./xml/ --outPath ./out/
```
