# -*- coding: utf-8 -*-
import pandas as pd
from tqdm import tqdm
import os
import requests
import numpy as np
import time
import pypdf
from langchain_core.output_parsers import StrOutputParser
# os.environ["GROQ_API_KEY"]
from pyscopus import Scopus
from langchain_groq import ChatGroq
#Used to filter out irrelevant information such as line numbers, author list, references list etc...
llama3 = ChatGroq(model="llama3-8b-8192") 
txt_filter_prompt = '''
Here is text from a page of a scientific article which was extracted from a pdf file. It may contain unwanted artefacts and information, such as line numbers, authors list, 
information about the editor or references list. Remove all unwanted information and give the exact text of the original scientific article, so that it can easily be stored in
a database. Do not alter the original meaning or phrasing. Do not add any extra word before the cleaned text.
 '''

#%%
class RecommendationDatabase():
    def __init__(self, 
                 db_path, 
                 LLM = llama3,
                 text_filter_prompt = txt_filter_prompt,
                 scopus_key = '1d900b79093e18e6ab42f0de039764e9'
                 ):
        self.db_path = db_path
        self.metadata_columns_labels = ['scopus_id', 'title', 'publication_name', 'issn', 'isbn', 'eissn',
               'volume', 'page_range', 'cover_date', 'doi', 'citation_count',
               'affiliation', 'aggregation_type', 'subtype_description', 'authors',
               'full_text']
        self.text_column_labels = ['doi', 'chunk_id','txt']
        self.metadata_path = os.path.join(self.db_path, 'metadata.pickle')
        self.text_path = os.path.join(self.db_path, 'text.pickle')
        try:
            self.db_metadata = pd.read_pickle(self.metadata_path)
            self.db_text = pd.read_pickle(self.text_path)
        except FileNotFoundError:
            os.makedirs(self.db_path, exist_ok=True)
            print(f'No existing data base found on the given path {self.db_path}. Creating new database.')
            self.db_metadata = pd.DataFrame(columns = self.metadata_columns_labels)
            self.db_text = pd.DataFrame(columns = self.text_column_labels)
        self.scopus_key = scopus_key
        self.scopus = Scopus(self.scopus_key)
        self.LLM_model = LLM
    
    def add_documents_from_scopus(self, search_str, search_kwargs):
        new_df = self.scopus.search(search_str, **search_kwargs)
        n_new_docs = new_df.shape[0]
        li_dois = list(self.db_metadata['doi'])
        for k in range(n_new_docs):
            if new_df.iloc[k]['doi'] not in li_dois:
                u = new_df.iloc[[k]][self.metadata_columns_labels]
                self.db_metadata = pd.concat((self.db_metadata,
                                                    u, ), ignore_index = True)
        return None
    
    def add_documents_from_pdf(self):
        pdf_path_ = os.path.join(self.db_path, 'raw_pdf')
        li_dois = list(self.db_metadata['doi'])
        for fi in os.listdir(pdf_path_):
            fi_path = os.path.join(pdf_path_, fi)
            doi = fi.replace('.pdf','').replace('_','/')
            if doi not in li_dois:
                new_df = pd.DataFrame(data = [[None for k in range(len(self.metadata_columns_labels))]],
                                      columns = self.metadata_columns_labels)
                new_df.loc[0,'doi'] = doi
                new_df.loc[0,'full_text'] = f'LocalFile--{fi_path}'
                self.db_metadata = pd.concat((self.db_metadata,
                                              new_df),
                                             ignore_index = True)
            elif self.db_metadata['full_text'] is None:
                self.db_metadata['full_text'] = f'LocalFile--{fi_path}'
        return None
    
    
    
    def check_local_documents(self):
        n_docs = self.db_metadata.shape[0]
        li_dois=list(self.db_text['doi'])
        for k in range(n_docs):
            met = self.db_metadata.iloc[k]
            doi = met['doi']
            if met['full_text'] is not None:
                if 'LocalFile--' in met['full_text']:
                    print(f'\n============= Checking {doi}')
                    try:
                        fi_path = met['full_text'].replace('LocalFile--','')
                        reader = pypdf.PdfReader(fi_path)
                    except FileNotFoundError:
                        print(f'''Metadata indicates this file is stored locally but it was not found on the specified
                              path {fi_path}. Deleting it from the database. ''')
                        rows_idx = np.array([k for k in range(n_docs)])
                        rows_to_drop = rows_idx[self.db_metadata['doi']==doi]
                        self.db_metadata.drop(labels = list(rows_to_drop), axis = 0, inplace = True)
                        
                        rows_idx = np.array([k for k in range(self.db_text.shape[0])])
                        rows_to_drop = rows_idx[self.db_text['doi']==doi]
                        self.db_text.drop(labels = list(rows_to_drop), axis = 0, inplace = True)
        return None

    def update_text(self, chunk_size = 5000, force_update = False):
        n_docs = self.db_metadata.shape[0]
        li_dois=list(self.db_text['doi'])
        for k in range(n_docs):
            met = self.db_metadata.iloc[k]
            doi = met['doi']
            print(f'\n============= Trying to add {doi}')
            if (doi not in li_dois) or force_update:
                if met['full_text'] is not None:
                    if 'LocalFile--' in met['full_text']:
                        try:
                            fi_path = met['full_text'].replace('LocalFile--','')
                            reader = pypdf.PdfReader(fi_path)
                            nop = len(reader.pages)
                            print('Number of pages : ', nop)
                            for jp,p in tqdm(enumerate(reader.pages)):
                                txt = p.extract_text()
                                proc_txt = self.__process_txt_chunk(txt)
                                new_df = pd.DataFrame(data = [[None for k in range(len(self.text_column_labels))]],
                                                      columns = self.text_column_labels)
                                if (doi not in li_dois):
                                    new_df.loc[0,'doi'] = doi
                                    new_df.loc[0,'chunk_id'] = jp
                                    new_df.loc[0,'txt'] = proc_txt
                                    self.db_text = pd.concat((self.db_text, new_df),ignore_index = True)
                                else:
                                    self.db_text.loc[k,'doi'] = doi
                                    self.db_text.loc[k,'chunk_id'] = jp
                                    self.db_text.loc[k,'txt'] = proc_txt
                        except FileNotFoundError:
                            print(f'''Metadata indicates this file is stored locally but it was not found on the specified
                                  path {fi_path}. Deleting it from the database. ''')
                            rows_idx = np.array([k for k in range(n_docs)])
                            rows_to_drop = 0 #rows_idx[np.array(list(self.))]
                            self.db_metadata.drop
                            self.db_text.loc[self.db_text['doi'] == doi]
                    else:
                        # Use scopus API to get utf-8 encoded text
                        try:
                            req = requests.get(met['full_text'], params={'apikey': self.scopus_key,
                                                                     'httpAccept': 'text/plain'}
                                            )
                            scp_txt = str(req.content, encoding = 'utf-8')
                            start = 0
                            end = 0
                            chunk_id = 0
                            n_chunks = len(scp_txt)//chunk_size
                            print(f'Number of chunks to process: {n_chunks}')
                            while end < len(scp_txt):
                                print('Currently processing chunk number ', chunk_id)
                                end = min(len(scp_txt), start + chunk_size)
                                chunk = scp_txt[start:end]
                                proc_txt = self.__process_txt_chunk(chunk)
                                new_df = pd.DataFrame(data = [[None for k in range(len(self.text_column_labels))]],
                                                      columns = self.text_column_labels)
                                if (doi not in li_dois):
                                    new_df.loc[0,'doi'] = doi
                                    new_df.loc[0,'chunk_id'] = chunk_id
                                    new_df.loc[0,'txt'] = proc_txt
                                    self.db_text = pd.concat((self.db_text, new_df),ignore_index = True)
                                else:
                                    self.db_text.loc[k,'doi'] = doi
                                    self.db_text.loc[k,'chunk_id'] = chunk_id
                                    self.db_text.loc[k,'txt'] = proc_txt
                                self.db_text = pd.concat((self.db_text, new_df),ignore_index = True)
                                start = end
                                chunk_id+=1
                    
                        except: #TODO: properly handle this error
                            print('''Could not download the full view. This is likely because your instution does not have access to it.''')
                    print('Succesfully added.')
                            
                else:
                    print('Full text not available.')
            else:
                print('This document has already been processed. Skipping it.')
        return None
            
    def __process_txt_chunk(self, chunk_txt):
        if self.LLM_model is not None:
            try:
                txt = self.LLM_model.invoke(txt_filter_prompt+'\n'+chunk_txt)
            except:
                time.sleep(2)
                txt = self.LLM_model.invoke(txt_filter_prompt+'\n'+chunk_txt)
            return StrOutputParser().invoke(txt)
        else:
            return chunk_txt
    
    def save(self):
        self.db_metadata.to_pickle(self.metadata_path)
        self.db_text.to_pickle(self.text_path)
        return None
        

            