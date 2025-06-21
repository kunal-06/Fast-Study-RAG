from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone,exceptions
import os,requests,socket,json,random
from urllib.error import URLError
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage,SystemMessage
from dotenv import load_dotenv
load_dotenv()

def Gemini_Query(message):
    try:
        gemini_model = init_chat_model(model="gemini-2.0-flash",model_provider="google_genai")
        result_mes = gemini_model.invoke(message)
        return [True,result_mes.content]
    except ConnectionError:
        return [False,'Error,Please Check Your Internet']   
    

def Chat_Query(query,namespaces):
    if query:
        index_name='rag-embedding-index'
        sentence="" 
        try:
            os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINIKEY") 
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            index = pc.Index(index_name)
            query_vector = embeddings.embed_query(query,output_dimensionality=384)
            for i in namespaces: 
                result = index.query(vector=query_vector, top_k=2, include_metadata=True,namespace=i)
                print(result)
                for j in result.matches:
                    sentence+=j.metadata['text']
        except (requests.exceptions.ConnectionError,socket.gaierror,URLError) as e:
            return 'Connection Error,Please Check Your Internet'   
        except exceptions.PineconeException:
            return 'Pinecone Server error'
        except exceptions.PineconeApiException:
            return 'Api Connection error'
        except Exception:
            print('Execption')
            return 'Something Gone Wrong !!!' 

        message=[
             SystemMessage(f'''you are working as chatbot which gives answer to users question,
             take referance of below provided sentences to give answer that fit apperoprite accourding to you,
             if answer is not present but a related context present in sentence then explain what is it about and start with this :" the answer of X dose not contains in your provided document but it has related content Y, Z" (here X is what is user asked,Y is what topic is provided in sentance related to question,Z is Explain that topic.)
             if answer is not present nor any related context in below sentence object just give output='your provided document dose not content this topic plese ask from give document',
             if there is code in answer use markdown/html for that, other should be as it is.
             and do not add additional formating give it in simple format.
             sentences : {sentence}'''),
             HumanMessage(query)    
        ]
        result_mes = Gemini_Query(message)
        return result_mes[1]
    else:
        return "You Provided Empty Text !!!"


def Generate_Quiz(filename):
    text = ''
    all_ids = []
    pagination_token = None
    index_name='rag-embedding-index'
    try:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(index_name)

        while True:
            results = index.list_paginated(namespace=filename,pagination_token=pagination_token)
            all_ids.extend([item["id"] for item in results["vectors"]])
            pagination_token = results.get("pagination",{}).get("next")
            if not pagination_token:
                break
        
        random_ids = random.choices(all_ids,k=15)
        result = index.fetch(ids=random_ids,namespace=filename)
        for i in random_ids:
            text= text + result.vectors[i].metadata['text']+" "
    except (requests.exceptions.ConnectionError,socket.gaierror,URLError) as e:
        return 'Connection Error,Please Check Your Internet' 

    message=[
        SystemMessage(f'''you are helpfull assistant,
        your task is to create MCQ's From Given [sentences],
        Return MCQ's Only with Valid Json Serialized fromat,  
        in the question options should be shuffled, so more option answer not come on same position(like all question's answer should not on 1st position or 2th or repeating)
        question should be meaning full,
        if below text is not enough to generate MCQ's do below things
         - from asked amount if only few are remaining then generate MCQ's which should be related to [sentences]
         - if more are remaining generate near amount that is multiple of 5 from asked amount ( asked:20, can generate:13 , give:15 ,   generate remaning 2 to make 15)   
        
        template:
                [
                 {"{"}
                    question:string,
                    options:array[string],
                    answer:string,
                    explanation:string
                 {"}"},
                ] 
        sentences : {text}'''),
        HumanMessage("Generate 10 MCQ question from given text") 
    ]
    result_mes = Gemini_Query(message)[1]
    content = json.loads(str(result_mes.replace("```"," ").replace("json"," ")))
    return [True,content]
    
  

def Generate_Card(filename):
    text = ""
    all_ids = []
    pagination_token = None
    index_name='rag-embedding-index'
    try:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(index_name)

        while True:
            results = index.list_paginated(pagination_token=pagination_token,namespace=filename)
            all_ids.extend([item["id"] for item in results["vectors"]])
            pagination_token = results.get("pagination",{}).get("next")
            if not pagination_token:
                break
        
        random_ids = random.choices(all_ids,k=15)
        result = index.fetch(ids=random_ids,namespace=filename)
        for i in random_ids:
            text = text + result.vectors[i].metadata['text']+" "
    except (requests.exceptions.ConnectionError,socket.gaierror,URLError) as e:
        return 'Connection Error,Please Check Your Internet' 

    message=[
        SystemMessage(f'''you are helpfull assistant,
        your task is to create Definations From Given [sentences],
        take importent word that explanotery or any word which has fullform in the [sentences],  
        return word with it's Defanition or Explanation, or it's Fullform, 
        maximum amount you should return is 10,
                
        Here a Example 1 : [word:'computer',answer: 'A computer is an electronic device that stores and processes information, following instructions. It can input, process, store, and output data like words, numbers, and pictures. In simple terms, a computer is a tool that can do calculations, solve problems, and perform other tasks based on the data and instructions given to it. ']              
        Here a Example 2 : [word:'www',answer:'World Wide Web']
        
        both ratio should be near to equal(like out of 10, 5 hould be fullforms and others are Explanation at random order)
        
        return the answer accourding to template,
        template:
                [
                 {"{"}
                    word:string,
                    answer:string
                 {"}"},
                ] 
        sentences : {text}'''),
        HumanMessage("Generate 10 Example from given text") 
    ]

    result_mes = Gemini_Query(message)
    if result_mes[0]:
        cards = json.loads(str(result_mes[1].replace("```"," ").replace("json"," ")))
        return [True,cards]
    