# linklabpublications
This project is used to provide a publication site that shows the publication work from all the faculty members in Link Lab community.

We introduce the LinkLabPublications HTMLs Generator, which is the hightlight of the project. It is a Python-based script that could generate all the static HTMLs files that the Link Lab Publications Site needs. The benefit of this way of implementation is because it is eaiser to get the site to the [UVA Link Lab Official Website](https://engineering.virginia.edu/labs-groups/link-lab). 

## Overview
### BibBase
We use [BibBase](https://bibbase.org/) to help create and manage our publications page. It is an online platform and you will have more information from their [documantation](https://bibbase.org/documentation) to learn how Link Lab publications pages are maintained and produced with the help of BibBase.

## Project Directory
1. OpenAlex_bibtex_mod.py

This Python code is an improved version from the source code [LinkLabScholarlyMetrics](https://github.com/epurpur/LinkLabScholarlyMetrics). We implement this file to create and keep the latest version of the bib.file for the Link Lab publications.

```
python3 OpenAlex_bibtex_mod.py
```

2. Link_Lab_Publications.bib

This bib file is generated after running the ```OpenAlex_bibtex_mod.py``` that is mentioned above. We will upload this file to amazing BibBase to create the publications



3. pythonHTMLGen

It is the highlight of the project. In the folder, you will run the Python file ```llpub_html_gen.py``` to generate the Link Lab Publication HTML Pages



```
pyhon3 llpub_html_gen
```

4. platform (optional)

It is the previous version and is implemented by ```Django``` web framework. It is now not a good option for making Link Lab Publication Site as it is harder for the maintenance later.

## How to use BibBase
#### Access the bib.file on BibBase file manager
The first step is to register an account on BibBase and then you are good to upload the bib.file, which includes the all collected publications from Link Lab faculty members.

#### Get the BibBase_URL

| [BibBase File Manager](https://bibbase.org/network/editor/files) | 
| -------- | 
|  <img width="600" alt="截圖 2024-04-09 下午9 24 45" src="https://github.com/AustinFengYi/linklabpublication/assets/22648364/2db58857-2679-470f-91a7-a20075aacd74">|
|<img width="600" alt="截圖 2024-04-09 下午9 24 09" src="https://github.com/AustinFengYi/linklabpublication/assets/22648364/97f808b6-e00a-4766-8502-1df6ccf8030c">|



## Quickstart
#### Prerequisites
Versioning
- python==3.8.5

#### Installation
Setup
1. Install [Python](https://www.python.org/downloads/)
2. Clone the repository
```
https://github.com/AustinFengYi/linklabpublication.git
```

#### Experiment on your machine (local environment)
This repository includes the folder named ```pythonHTMLGen``` , to start to experiment on your local machine with our repo.

1. Go to the folder ```pythonHTMLGen```, then command the following
```
pip3 install requirements.txt
python3 llpub_html_gen.py
```
<img width="620" alt="upload_755abcd180e275a65ac4826a5881bf53" src="https://github.com/AustinFengYi/linklabpublication/assets/22648364/63326b6f-1310-4776-89e0-9448064e97dc"> <br>

2. If working successful, in terminal you will see the results like the below.

<img width="655" alt="upload_755abcd180e275a65ac4826a5881bf532" src="https://github.com/AustinFengYi/linklabpublication/assets/22648364/4169b7f1-cb89-4506-9f45-71fec3d5ccef"> <br>

3. If working successful, in folder ```pythonHTMLGen``` you will see the files structured like the below.



4. Finally, we can browse the publication site through node.js (express.js). Run the following command in the directory path

![ezgif-1-724e9e9fd0](https://github.com/AustinFengYi/linklabpublication/assets/22648364/99c73bfd-abd6-4243-a7d4-a574918db71c)

```
node app.js
```


## How to Maintain the Project
#### Step 1: Keep the latest version of bib file 
[Directory: OpenAlex_bibtex_mod.py]

TBD...

#### Step 2: Maintain the bib file of Link Lab Publications on [BibBase](https://bibbase.org/)'s file manager
[Bibbase File Manager](https://bibbase.org/network/editor/files)

TBD...

#### Step 3: 
[Directory/PythonGen: llpub_html_gen.py]

In the file ```llpub_html_gen.py```, notice the following variables
```python
bibbase_url = "" # string
# 
filter_years = []  # array
# 
filter_authors = {} # dict 
```

1. bibbase_url=
Here if puts the URL of the bib file on BibBase  
2. filter_year
Here it puts the year range of the publications
3. filter_authors
Here it is announced as the dictionary of the [key:pair] 
```author_name: author_searh_name_in_BibBase_filter_condition```

Notice that the list of Link Lab faculty members is referenced from the released [ORICID spreadsheet](). 

After having the lateast bib file content on Bibbase File Manager, we can run the command to generate the newest static html files for the Link Lab publication site.
```
python3 llpub_html_gen.py
```

