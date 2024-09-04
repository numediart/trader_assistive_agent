# -*- coding: utf-8 -*-
import uuid
from tqdm import tqdm
import os
import time
import json
import pypdf
from langchain_core.output_parsers import StrOutputParser
# os.environ["GROQ_API_KEY"]
from langchain_groq import ChatGroq
llama3 = ChatGroq(model="llama3-8b-8192") #Used to filter out irrelevant information such as line numbers, author list, references list etc...
txt_filter_prompt = '''
Here is text from a page of a scientific article which was extracted from a pdf file. It may contain unwanted artefacts and information, such as line numbers, authors list, 
information about the editor or references list. Remove all unwanted information and give the exact text of the original scientific article, so that it can easily be stored in
a database. Do not alter the original meaning or phrasing.
 '''


#TODO: Handle the case where a pdf file is deleted from disk
# Currently its text stays in the csv: the correct behavior should be to delete it
# One way could be to directly store the information in a pandas dataframe instead of csv
#%%
def GetArticles(base_path):
    metadata_path = os.path.join(base_path, 'metadata.json')
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print('''Completing existing database. 
              If you wish to erase the previous database do so manually.''')
    except FileNotFoundError:
        print('''No metadata found. Building raw database from scratch. 
              ''')
        metadata = {}
        
    raw_path = os.path.join(base_path, 'raw_pdf')
    for di in os.listdir(raw_path):
        path_ = os.path.join(raw_path, di)
        for fi in os.listdir(path_):
            path_fi_ = os.path.join(path_, fi)
            key = f'{di}_{fi}'
            if not(key) in metadata.keys():
                metadata[key] = {}
                metadata[key]['path'] = path_fi_
    with open(metadata_path, 'w') as f:
        json.dump(metadata,f, indent = 2)
    return metadata


def ExtractText(metadata, base_path, 
                txt_filter_prompt = None, model = None, 
                ):
    all_txt = {}
    if model is not None:
        out_parser = StrOutputParser()
    li_articles = list(metadata.keys())
    for art in li_articles:
        all_txt[art] = {}
        print('\n\n============ New document ',art)
        fi = metadata[art]['path']
        if not('already_csved' in metadata[art].keys()) or not(metadata[art]['already_csved']):
            try:
                reader = pypdf.PdfReader(fi)
            except FileNotFoundError:
                print(f'File {fi} not found on disk. Removing it from metadata.')
                del metadata[art]
                continue
            nop = len(reader.pages)
            print('Number of pages : ', nop)
            for jp,p in tqdm(enumerate(reader.pages)):
                txt = p.extract_text()
                if model is not None:
                    q = f'{txt_filter_prompt}:\n {txt}'
                    try:
                        txt = model.invoke(q)
                    except:
                        time.sleep(1)
                        txt = model.invoke(q)
                    txt = out_parser.invoke(txt)
                all_txt[art][jp] = txt
            metadata[art]['already_csved'] = True
        else:
            print(f'It is already in the csv. Skipping it.')
    metadata_path = os.path.join(base_path, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata,f, indent = 2)
    return all_txt


def WriteTxtToCSV(all_txt, base_path, database_name):
    flat_txt = []
    for art in all_txt.keys():
        for c_idx in all_txt[art].keys():
            flat_txt.append(all_txt[art][c_idx].replace('\t', ' '))
    flat_txt = '\n\t'.join([c.replace('\t', ' ').replace('\r','').replace('\n', '') for c in flat_txt])
    with open(os.path.join(base_path, f'{database_name}.csv'), 'a', encoding = 'utf-8') as f:
      f.write(flat_txt)
    return None


            
            