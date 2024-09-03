from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
import os
import pandas as pd
# os.environ["GROQ_API_KEY"] 
from langchain_groq import ChatGroq
from types import SimpleNamespace
from tqdm import tqdm


class RAG:
    def __init__(self, csv_path, db_path, model,
                 embedding_function, csv_separator = '\t'):
        if csv_path is None and db_path is None:
            raise ValueError('Either csv_path or db_path needs to be specified')
        self.csv_path = csv_path
        self.db_path= db_path
        self.model = model
        self.embedding_function = embedding_function
        self.csv_separator = csv_separator
        self.retriever = None
        self.__load_chromadb()
        
        return None

    def __load_csv_to_documents(self):
        try:
            df = pd.read_csv(self.csv_path, encoding="utf-8", sep=self.csv_separator) #encoding="windows-1252"
        except Exception as e:
            print(f"Error reading the CSV file: {self.csv_path}")
            print(f"Exception: {e}")
            return []
        
        documents = []
        print('Total number of documents : ', df.shape[0])
        for index, row in tqdm(df.iterrows()):
            try:
                document = SimpleNamespace(
                    page_content=f"{row['Method Name']}: {row['Definition']}",
                    metadata={'method_name': row['Method Name']}
                )
                documents.append(document)
            except:
                document = SimpleNamespace(
                    page_content=f"{row[0]}",
                    metadata={}
                )
                documents.append(document)
        return documents
    
    def __load_chromadb(self):
        if os.path.exists(self.db_path):
            #print("Loading Chroma database")
            db = Chroma(persist_directory=self.db_path, embedding_function=self.embedding_function)
        else:
            if self.csv_path is None:
                raise FileNotFoundError('Did not find a cached database and no csv path provided.')
            print("No cached database found. Creating Chroma database.")
            documents = self.__load_csv_to_documents()
            db = Chroma.from_documents(documents=documents, 
                                       embedding=self.embedding_function, 
                                       persist_directory=self.db_path)
            db.persist()
        self.db = db
        return None
            
    def create_retriever(self, search_kwargs):
        # It is automatically called in retrieve_answer if the retriever has not been created manually
        # I leave the option to call it manually to be able to change the search_kwargs
        self.retriever = self.db.as_retriever(search_kwargs = search_kwargs)
        return None
    
    def retrieve_answer(self, question, print_context = False):
        template = """Answer the question based only on the following context:
        {context}
    
        Question: {question}
        """
        if self.retriever is None:
            self.create_retriever(search_kwargs = {'k':2,})
        if print_context:
            print(self.retriever.invoke(question))
        prompt = ChatPromptTemplate.from_template(template)
        chain = (
            {"context": self.retriever, 
             "question": RunnablePassthrough()}
            | prompt
            | self.model
            | StrOutputParser()
        )
        return chain.invoke(question)




