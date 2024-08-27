# -*- coding: utf-8 -*-
import pickle
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings

import os
import pandas as pd

# You might need to setup your grok api key
os.environ["GROQ_API_KEY"]  = ""

from langchain_groq import ChatGroq

from types import SimpleNamespace
from rag_utils import rag_utils as rag
#%%
base_path = './Data' #You might need to edit it
path_csv = os.path.join(base_path, 'raw_investopedia.csv')
db_name = os.path.splitext(os.path.basename(path_csv))[0] + '_db'
PERSIST_DIRECTORY = os.path.join(base_path, db_name)

llama3 = ChatGroq(model="llama3-8b-8192")
finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  # modèle entraîné sur des blogs financiers

#%%
# Automatically creates the database if it does not exist at PERSIST_DIRECTORY from the path_csv
# if the database already exists, the csv path is not used
db = rag.load_chromadb(PERSIST_DIRECTORY, finlang_embed, 
                       csv_dir = path_csv, separator = '\t') 

#%%
retriever = db.as_retriever(search_kwargs = {'k':3,})
# q = "What can you tell me about the 403(b) ?"
q = "What can you tell me about bankruptcy ?"
q = "What can you tell me about financial statements ? "
print(rag.retrieve_answer(q,
                      retriever,
                      llama3,
                      print_context = False))