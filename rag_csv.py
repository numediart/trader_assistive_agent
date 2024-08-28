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

PATH_CSV = 'Data/Financial_and_Technical_Analysis_Methods_t.csv'

db_name = os.path.splitext(os.path.basename(PATH_CSV))[0] + '_db.pkl'
PERSIST_DIRECTORY = os.path.join('Data', db_name)

llama3 = ChatGroq(model="llama3-8b-8192")
finlang_embed = HuggingFaceEmbeddings(model_name='FinLang/finance-embeddings-investopedia')  # modèle entraîné sur des blogs financiers

class data_obj(object):
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

def load_csv_to_documents(path_csv, separator='\t'):
    try:
        df = pd.read_csv(path_csv, encoding="windows-1252", sep=separator)
    except Exception as e:
        print(f"Error reading the CSV file: {path_csv}")
        print(f"Exception: {e}")
        return []
    
    documents = []
    for index, row in df.iterrows():
        try:
            document = SimpleNamespace(
                page_content=f"{row['Method Name']}: {row['Definition']}",
                metadata={'method_name': row['Method Name']}
            )
            documents.append(document)
        except Exception as e:
            print(f"Error processing line {index}: {row}")
            print(f"Exception: {e}")
    return documents

if os.path.exists(PERSIST_DIRECTORY):
    print("Loading Chroma database")
    db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=finlang_embed)
else:
    print("Creating Chroma database")
    documents = load_csv_to_documents(PATH_CSV)
    db = Chroma.from_documents(documents=documents, embedding=finlang_embed, persist_directory=PERSIST_DIRECTORY)
    db.persist()

retriever = db.as_retriever()

def retrieve_answer(question):
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llama3
        | StrOutputParser()
    )
    return chain.invoke(question)

if __name__ == "__main__":
    print(retrieve_answer("List five methods that are based on average calculation."))
