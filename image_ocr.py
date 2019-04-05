# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 14:09:08 2019

@author: eduardo

OCR utilizado em imagens do museu das missões
"""
try:  
    from PIL import Image
except ImportError:  
    import Image
import pytesseract
import os
from tqdm import tqdm

path = "C:\\path_to_the_folder_where_images_are_stored"

# https://github.com/UB-Mannheim/tesseract/wiki preciso instalar caso esteja utilizando o Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" 

def ocr_core(filename):  
    """
    This function will handle the core OCR processing of images.
    Pt = para utilizar o lang = "por" é preciso baixar o arquivo por.taineddata do link: https://github.com/tesseract-ocr/tessdata
    o arquivo deve ser colocado na pasta: C:\Program Files (x86)\Tesseract-OCR\tessdata
    """
    img = Image.open(filename)
    img.load()
    text = pytesseract.image_to_string(img, lang="por")
    return text

list = []
for filename in tqdm(os.listdir(path), desc="processando dados", unit="files"):
    if filename.endswith('.jpeg'):
        file = path + filename
        list.append(ocr_core(file))

# Todo o texto em uma única lista.
res = "".join(list)
