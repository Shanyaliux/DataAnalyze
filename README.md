### Install

```bash
pip install -r requirements.txt
```

### Usage

```bash
python DataAnalyze.py ${type} ${path}
```
>'type' is the format of the dataset, optional 'coco' or 'voc'.  
If 'type' is 'coco', the 'path' is the json file path.  
If 'type' is 'voc', the 'path' is the path of the xml file directory.

#### Example
```bash
python DataAnalyze.py coco ./tarin.json
```

```bash
python DataAnalyze.py voc ./xml/
```
