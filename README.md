# Master's Thesis
This repository contains source files for my thesis at the VU, titled "Enhancing Platform Navigability at [...]: Improving Information Hierarchy through Entity Linking".

## Description
This package includes a method to automatically find related medical information for a certain disease, symptom or sign, using entity linking with medical knowledge bases SNOMED and ICPC, resulting in an interconnected network of related information. 

## Installation
One can download the necessary SNOMED database at [here](https://surfdrive.surf.nl/files/index.php/s/jtF1auvFjVIqbT7). The ICPC database can be downloaded at [here](https://www.nhg.org/praktijkvoering/informatisering/nhg-tabellen-voor-in-his/icpc/). After downloading, place these databases in the `data` folder. 
After this, an SQLite database should be created from these terminologies, to facilitate fast and effocoemt data retrieval. 

## Credits
The EntityLinking method used in this project is developed by dr.ir. Majud Mohammadi, available at [here](https://github.com/Majeed7/EntityLinking). It is adapted for this specific project.

## Visualization
The file `visualization.py` contains a script to create a disease network, to provide a more intuitive understanding of the results. 

## Requirements
```
numpy==1.22.4
pandas==1.4.4
requests==2.22.0
scipy==1.12.0
matplotlib==3.8.3
seaborn==0.13.2
gensim==4.2.0
nltk==3.6.5
spacy==3.2.4
joblib==1.3.2
```

## Usage
First, one creates the database to store all the results with `creatingdatabase.py`. Then, `insertingdatabase.py` is used to insert the results of every step of the entity linking method. To create a list of the related information per case, `findfinallinks.py` is used. 

## Private Data Notice
This project relies on private data that is not included in this repository. You will need access to this data to fully utilize the project.

## Data Description
Data Type: Data from the content management system (CMS).
Data Source: Thuisarts.
Access Requirements: Specific credentials or permissions are required to access the data from Thuisarts.