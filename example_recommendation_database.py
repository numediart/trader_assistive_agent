# -*- coding: utf-8 -*-
# Example on how to use the RecommendationDatabase class from recommendation_db_utils.py
# You might need to setup your grok api key
# os.environ["GROQ_API_KEY"]
from langchain_groq import ChatGroq

import sys
path_ = "E:/github/multisensor_llm"
if not(path_ in sys.path):
    sys.path.insert(0,path_)
from rag_utils import recommendation_db_utils as redu

#%%
# This is used to format the text before storing it in the database, removing unwanted information coming from scrapping
# The model can be none to avoid preprocessing altogether (the raw text is then used)
llama3 = ChatGroq(model="llama3-8b-8192") 

# Initialize the object
db = redu.RecommendationDatabase('E:/github/multisensor_llm/Data/Recommendation', LLM = None)

# visit http://zhiyzuo.github.io/python-scopus/doc/quick-start.html and https://dev.elsevier.com/tecdoc_text_mining.html to learn more about the scopus api 
# The database can be populated from the scopus api
db.add_documents_from_scopus('KEY(Fear of missing out)', {'count':5}) # Scraps scopus according to the search_str and adds the documents to the metadata

# The database can be populated from pdf files place in /Data/Recommendation/raw_pdf
# The name of the pdf should be the doi of the scientific article where '/' has been replaced by '_'
# the doi is used as a unique identifier to keep track of the document in the database
db.add_documents_from_pdf() # Adds the documents in raw_pdf to the metadata if they are not present in it

# Update the text.pickle (needs to be run after adding documents)
# If force_update is False it does not reprocess the documents already found in the database
# It could be useful to force_update if you change the filtering prompt or model for instance
db.update_text(force_update = False) 

 # Deletes the docuemnts from text.pickl and metadata.pickle if they are no longer on disk
db.check_local_documents()

# save to pickle files
db.save() 

