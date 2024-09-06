from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import pandas as pd
# os.environ["GROQ_API_KEY"] 
from types import SimpleNamespace
from tqdm import tqdm


class RAG:
    def __init__(self, dataframe_path, db_path, model,
                 embedding_function):
        # The dataframe needs to have one column titled 'text' which contains the text used to perform retrieval
        # It is also the text fed to the LLM after context retrieval
        # The other columns are propagated to the chroma_db as metadata and can be arbitrary
        # For instane, database created with the RecommendationDatabase class propagates the DOI of
        # the article from which the text comes
        if dataframe_path is None and db_path is None:
            raise ValueError('Either dataframe_path or db_path needs to be specified')
        self.df_path = dataframe_path
        self.db_path= db_path
        self.model = model
        self.embedding_function = embedding_function
        self.retriever = None
        self.__load_chromadb()
        
        return None

    def __load_dataframe_to_documents(self):
        try:
            df = pd.read_pickle(self.df_path) #encoding="windows-1252"
        except Exception as e:
            print(f"Error reading the CSV file: {self.csv_path}")
            print(f"Exception: {e}")
            return []
        
        documents = []
        print('Total number of documents : ', df.shape[0])
        columns_label = [c for c in df.columns if c!='txt']
        for index, row in tqdm(df.iterrows()):
            met = dict(df.iloc[index][columns_label])
            content = df.iloc[index]['txt']
            document = SimpleNamespace(
                page_content=content,
                metadata=met
            )
            documents.append(document)
        return documents
    
    def __load_chromadb(self):
        
        if os.path.exists(self.db_path):
            #print("Loading Chroma database")
            db = Chroma(persist_directory=self.db_path, embedding_function=self.embedding_function)
        else:
            if self.df_path is None:
                raise FileNotFoundError('Did not find a cached database and no dataframe path provided.')
            print("No cached database found. Creating Chroma database.")
            documents = self.__load_dataframe_to_documents()
            db = Chroma.from_documents(documents=documents, 
                                       embedding=self.embedding_function, 
                                       persist_directory=self.db_path)
            db.persist()
        self.db = db
        return None
      
    # TODO: The below code creates duplicates
    # def update(self):
    #     documents = self.__load_csv_to_documents()
    #     for doc in documents:
    #         self.db.add_documents(doc)
    #     return None
        
    def create_retriever(self, search_kwargs):
        # It is automatically called in retrieve_answer if the retriever has not been created manually
        # I leave the option to call it manually to be able to change the search_kwargs
        self.retriever = self.db.as_retriever(search_kwargs = search_kwargs)
        return None
    
    def retrieve_answer(self, question, max_context = 20000, print_context = False):
        template = """Answer the question based with the help of the following context:
        {context}
    
        Question: {question}
        """
        if self.retriever is None:
            self.create_retriever(search_kwargs = {'k':10,})
        documents = self.retriever.invoke(question)
        context = '. '.join([d.page_content for d in documents])
        if print_context:
            print(context)
        prompt = ChatPromptTemplate.from_template(template)
        chain = (
            {"context": lambda x:context[:max_context], 
             "question": RunnablePassthrough()}
            | prompt
            | self.model
            | StrOutputParser()
        )
        retrieve_out = chain.invoke(question)
        try:
            dois = set([documents[k].metadata['doi'] for k in range(min(len(documents),3))])
            manual_output = f'''The following scientific articles were found to be relevant if you wish to get additional information: {dois}'''
        except KeyError:
            manual_output = ''
        return retrieve_out+'\n'+manual_output
    
    





