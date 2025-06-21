import os
from dotenv import load_dotenv
import requests
import socket
from urllib.error import URLError
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone,ServerlessSpec
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import re


def vector_embedding(filename):
    filepath = 'pdfs/'+filename
    loader = PyPDFLoader(filepath)
    texts = []
    embedding = []
    pdf_metadata={}
    docs = loader.load()

    metadata =  docs[0].metadata
    pdf_metadata = {
        'file_name':metadata['source'].split("/")[-1],
        'title':metadata['title'],
        'create_date':metadata['creationdate'].split("T")[0],
        'total_page':metadata['total_pages'],
    }
    print("metadata done...")
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=0
        )
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINIKEY") 
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        for doc in docs:
            text = doc.page_content
            text = re.sub(' +',' ',text) 
            text = re.sub('\n+',' ',text)
            text = re.sub('\t+',' ',text)
            chunk = text_splitter.split_text(text)
            texts += chunk
        embedding = embeddings.embed_documents(texts,output_dimensionality=384)

        print("Embedding done...",len(texts),len(embedding),type(embedding[0]))
    except (requests.exceptions.ConnectionError,socket.gaierror,URLError) as e:
        return {'status':False,'message':"Check Your Internet Connection"}
    except Exception:
        return {'status':False,'message':"Some thing Want Wrong !!!"}
    
    try:
        load_dotenv()
        
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index_name='rag-embedding-index'
        print(index_name)
        dimension = len(embedding[0])

        items_to_upsert = [
            (f'{pdf_metadata['file_name']}-{i}',vector,{'text':text}) 
            for i, (text,vector) in enumerate(zip(texts,embedding))
        ]
        if index_name not in pc.list_indexes().names():
            pc.create_index(name=index_name,dimension=dimension,spec=ServerlessSpec(
                cloud="aws",          
                region="us-east-1"
            ))

        index = pc.Index(index_name)
        index.upsert(items_to_upsert,namespace=filename)
        print("Index done...")
        return {'status':True}
    except (requests.exceptions.ConnectionError,socket.gaierror,URLError) as e:
        return {'status':False,'message':"Check Your Internet Connection"}
    except Exception:
        return {'status':False,'message':"Some thing Want Wrong !!!"}

def Delete_Vector(filename):
    try:
        load_dotenv()
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index_name='rag-embedding-index'
        index = pc.Index(index_name)
        index.delete(delete_all=True,namespace=filename)
        return [True,"Delete Successfully"]
    except (requests.exceptions.ConnectionError,socket.gaierror,URLError) as e:
        return [False,"Check Your Internet Connection"]
    except Exception:
        return [False,"Some thing Want Wrong !!!"]
    
