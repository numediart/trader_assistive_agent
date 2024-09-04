# -*- coding: utf-8 -*-
import sys
import os
path_ = "E:/github/multisensor_llm"
if not(path_ in sys.path):
    sys.path.insert(0,path_)
from rag_utils import db_behavior_utils as dbbu

# This script updates the csv and metadata.json of the behavior RAG database
# It must be run to take into account newly added document
# New documents (in pdf format) should be added in ./Data/behavior/raw_pdf/Folder/new_document.pdf
# Folder can be whatever you want ; for now the Folder name you choose is not very important
# Later on, it may be interesting to use it to propagate metadata informations to the chromadb 
# (eg. the topic of the document for instance)
#%%
base_path = os.path.join(path_, 'Data', 'behavior')
metadata = dbbu.GetArticles(base_path)
all_text_chunks = dbbu.ExtractText(metadata, base_path, 
                              model = dbbu.llama3,txt_filter_prompt = dbbu.txt_filter_prompt
                              )
dbbu.WriteTxtToCSV(all_text_chunks, base_path, 'behaviour_database_v0')
