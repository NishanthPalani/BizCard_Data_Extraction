# BizCard_Extraction - Extracting Business Card Data by using easyOCR (Optical image Character Recognition)

## Project Overview

BizCardX is a user-friendly tool for extracting information from business cards. The tool uses EC-OCR technology to recognize text on business cards and extracts the data and then loads to a SQL database with user authentication. Users can access the extracted information using a GUI built on streamlit app. If user wishes to alter any of the data they can visit the modification page and select their preferance for modification. This will give user an upper hand in both modification and deleting the data they want.

## Libraries/Modules used for the project!

1. Pandas - (To Create a DataFrame with the scraped data)
1. mysql.connector - (To store and retrieve the data)
1. Streamlit - (To Create Graphical user Interface)
1. EasyOCR - (To extract text from images)
1. NGROK - (To build a bridge to execute the teamlit python code and Google Colab)

## *Packages used*

Below Packages were used to code the project
```python
- import os
- import streamlit as st
- import pandas as pd
- import numpy as np
- from streamlit_option_menu import option_menu
- import easyocr
- from PIL import Image
- import cv2
- import re
- import sqlite3
```

