# from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# import getpass
# import os

# os.environ["GROQ_API_KEY"] = getpass.getpass()

from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer

PATH_CSV = ''
llama3 = ChatGroq(model="llama3-8b-8192")
finlang_embed = SentenceTransformer('FinLang/investopedia_embedding') #replace this with model trained on finance blogs

llm = llama3()
embedding_function = finlang_embed()

loader = CSVLoader(PATH_CSV, encoding="windows-1252")
documents = loader.load()

db = Chroma.from_documents(documents, embedding_function)
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
        | llm
        | StrOutputParser()
    )
    return chain.invoke(question)