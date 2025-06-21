import streamlit as st
import os
from streamlit.components.v1 import html
from pinecone import Pinecone
from retrivedata import Chat_Query,Generate_Quiz,Generate_Card
from vector_store import vector_embedding,Delete_Vector
from google import genai

st.set_page_config(page_title="Faststudy", layout="centered")

index_name='rag-embedding-index'

if "verified" not in st.session_state:
    st.session_state.verified = False

def verify_keys():
    key1 = st.session_state.get("key1", "").strip()
    key2 = st.session_state.get("key2", "").strip()
    
    # Add your verification logic here
    if key1 and key2:
        try:
            pc = Pinecone(api_key=key1)
            pc.list_indexes()
            client = genai.Client(api_key=key2)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents="How Are You?"
            )
            st.session_state.verified = True
            os.environ["PINECONE_API_KEY"] = key1
            os.environ["GOOGLE_API_KEY"] = key2
            st.toast(icon="✅",body="API keys verified!")
        except Exception as e:
            st.session_state.verified = False
            st.error(icon="❌",body="Please enter Valid API Key !!")
    else:
        st.error(icon="❌",body="Please enter both API keys.")

if "namespaces" not in st.session_state:
    st.session_state.namespaces=[]

if not st.session_state.verified:
    st.markdown(
        """
        <style>
        .main > div {pointer-events: none; opacity: 0.3;}
        #api-form {pointer-events: auto !important; opacity: 1 !important;}
        </style>
        """, unsafe_allow_html=True
    )
    
    with st.container():
        st.markdown('<div id="api-form">', unsafe_allow_html=True)
        st.header("🔐 Insert API Keys")
        st.text_input("Enter Pinecone API Key ", key="key1",type="password")
        cl1 = st.columns(3,vertical_alignment="center")
        cl1[0].text("Ckeck hear to create one !!")
        cl1[1].link_button(url="https://docs.pinecone.io/guides/get-started/quickstart",label="here")
        st.text_input("Enter Gemini API Key ", key="key2",type="password")
        cl2 = st.columns(3,vertical_alignment="center")
        cl2[0].text("Ckeck hear to create one !!")
        cl2[1].link_button(url="https://ai.google.dev/gemini-api/docs",label="here")
        
        st.button("Verify", on_click=verify_keys)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop() 

def get_namespaces():
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index(index_name)
    try:
        namespaces = index.describe_index_stats().namespaces.keys()
        print(namespaces)
        st.session_state.namespaces = namespaces
        return namespaces
    except Exception as e:
        print("Pinecone Error !!!")

def process_file(file,path):
    print(path)
    with open(path,'wb') as f:
        f.write(file.getbuffer())
        print("Saved :",file.name)
        st.write(file.name," is uploded ")
    
    
    with st.spinner("Creating Vector Embeddings ", show_time=True):
        response = vector_embedding(file.name)        
        if not response['status']:
            st.write(response['message'] + f', Please Reupload Your {file.name} File')
        st.success("Embeddings is Created")
    st.rerun()
        

def Home():

    st.title("📚 Faststudy")
    st.subheader("Smart Learning, Fast Answers.")

    st.markdown("""
    Welcome to **Faststudy** — your intelligent learning assistant.  
    Just upload your study material, and let AI help you:
    - ❓ **Ask Questions**
    - 🧠 **Generate Quizzes**
    - 💡 **Create Tip Cards**  
    """)

    st.divider()

    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📄 Upload PDFs")
        st.markdown("Import your study material with a click. All content is indexed for fast search.")

    with col2:
        st.markdown("### 🧾 Ask Anything")
        st.markdown("Get instant, AI-powered answers based on your documents.")

    with col3:
        st.markdown("### 🎯 Practice & Tips")
        st.markdown("Generate quizzes and concise tip cards to reinforce your learning.")

    st.divider()
    st.markdown("### 🚀 Get Started")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.button("📁 Upload Material")
    
    with col_b:
        st.button("🤖 Ask a Question")

    with col_c:
        st.button("🎓 Generate Quiz & Tips")

    
    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit | Powered by RAG")

def Upload_Metrial() :
    upload_folder = 'pdfs'
    st.title("Upload PDF's Here !")
    files = st.file_uploader(type='pdf',label="file_uploader",accept_multiple_files=True,label_visibility="hidden")
    for file in files:
        filepath = os.path.join(upload_folder,file.name)
        
        if file is not None and file.name not in (st.session_state.namespaces or get_namespaces()):
            process_file(file,filepath)
            print("Uploaded !!!!!")
        else:
            print(f"Skipped (already processed): {file.name}")
    st.markdown("<h4>List Of Uploaded Files !</h4>",unsafe_allow_html=True)
    
    try:
        for i in (st.session_state.namespaces or get_namespaces()):
            container1 = st.container(border=True,height=80)
            row1 = container1.columns(spec=[5, 1],vertical_alignment="center")
            row1[0].write(f"{i} File")
            if row1[1].button("Remove",key=i):
                response =  Delete_Vector(i)
                if response[0]:
                    st.write(i +" " + response[1])
                    get_namespaces()
                    st.rerun()
                else:
                    st.popover(response[0]) 
    except Exception as e:
        st.write("There is Error With Main File ")

def Chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if not st.session_state.namespaces:
        st.session_state.namespaces = get_namespaces()
    
    with st.container():
        st.markdown("""
            <style>
            .chat-box {
                display: flex;
                overflow-y: auto;
                max-height: 70vh;
                padding: 5px;
                margin-bottom: 10px;
                overflow:auto;
            }

            .message.bot {
                text-align: justify;
                margin-left:10px;
                margin-bottom:10px;
            }

            .message.user {
                align-self: flex-start;
                text-align: left;
                margin-left:10px;
    
            }

            .message {
                padding: 8px 12px;
                border-radius: 12px;
                word-wrap: break-word;
            }

            .chat-input-container {
                position: fixed;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 100%;
                max-width: 700px;
                padding: 0 10px;
                z-index: 9999;
                transition: background-color 0.3s ease;
                
            }

            .chat-input-container:hover {
                background-color: rgba(255, 255, 255, 0.8);
            }
            </style>
        """, unsafe_allow_html=True)

        
        st.title('Ask Question To Bot')
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        user_input = st.chat_input("Type your message",key="chat")
        st.markdown('</div>', unsafe_allow_html=True)
     
        if user_input:
            response = Chat_Query(user_input,st.session_state.namespaces)
            response.replace('/n','</br>')
            st.session_state.messages.append({"role": "bot", "content": "🤖 "+response})
            st.session_state.messages.append({"role": "user", "content": "🧑‍💻 "+user_input})
            st.rerun()
            

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages[::-1]:
        role = msg["role"]
        css_class = "user" if role == "user" else "bot"
        st.markdown(f'<div class="message {css_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
def Quizfy():
    if "page1" not in st.session_state:
        st.session_state.page1 = "Quizfy"
    if "quiz" not in st.session_state:
        st.session_state.quiz = []
    if "current_q" not in st.session_state:
        st.session_state.current_q = 0
    if "selected" not in st.session_state:
        st.session_state.selected = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    def reset_quiz():
        st.session_state.page1 = "Quizfy"
        st.session_state.quiz = []
        st.session_state.current_q = 0
        st.session_state.selected = {}
        st.session_state.submitted = False
        st.session_state.explanation = ''

    if st.session_state.page1 == "Quizfy":
        st.title("📝 Create a Quiz")
        processed_files = (st.session_state.namespaces or get_namespaces())
        for i in processed_files:
            container2 = st.container(border=True)
            row2 = container2.columns(spec=[5, 1],vertical_alignment="center")
            row2[0].write(f"Create Quize For {i} File")
            if row2[1].button("Generate",key=i):
                response=[]
                response=Generate_Quiz(i)
                quiz_data=[]
                if response[0]:
                    quiz_data=response[1]
                    st.session_state.quiz = quiz_data
                    st.session_state.page1 = "quiz"
                    st.rerun()
                else:
                    st.popover(response[0])

    elif st.session_state.page1 == "quiz":
        quiz = st.session_state.quiz
        current_q = st.session_state.current_q
        question_data = quiz[current_q]
        options = question_data["options"]
        correct_answer = question_data["answer"]
        st.session_state.explanation = question_data["explanation"]
        st.title(f"Question {current_q + 1} of {len(quiz)}")
        st.write(question_data["question"])

        key = f"q{current_q}_radio"

        if current_q not in st.session_state.selected:
            selected_option = st.radio(
                "Select an option:",
                options,
                index=None,
                key=key
            )

            if selected_option and st.session_state.get(key + "_locked") is not True:
                st.session_state.selected[current_q] = selected_option
                st.session_state[key + "_locked"] = True
                st.rerun()
        else:
            selected_option = st.session_state.selected[current_q]
            for opt in options:
                if opt == correct_answer:
                    st.markdown(f"✅ **{opt}**", unsafe_allow_html=True)
                elif opt == selected_option:
                    st.markdown(f"❌ {opt}", unsafe_allow_html=True)
                else:
                    st.markdown(f"- {opt}")
            st.markdown(f"<b>Explanation :</b> {st.session_state.explanation}",unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.session_state.current_q > 0:
                if st.button("Previous"):
                    st.session_state.current_q -= 1
                    st.rerun()
        with col2:
            if st.session_state.current_q < len(quiz) - 1:
                if st.button("Next"):
                    st.session_state.current_q += 1
                    st.rerun()
        with col3:
            if st.button("Cancel"):
                reset_quiz()
                st.rerun()

        st.markdown("---")
        if not st.session_state.submitted:
            if st.button("Submit Quiz"):
                st.session_state.submitted = True
                st.session_state.page1 = "result"
                st.rerun()

    elif st.session_state.page1 == "result":
        st.title("📊 Quiz Result")
        total = len(st.session_state.quiz)
        attempted = len(st.session_state.selected)
        correct = 0

        for i, q in enumerate(st.session_state.quiz):
            if i in st.session_state.selected and st.session_state.selected[i] == q["answer"]:
                correct += 1

        st.write(f"**Total Questions:** {total}")
        st.write(f"**Attempted:** {attempted}")
        st.write(f"**Total Marks:** {total}")
        st.write(f"**Gained Marks:** {correct}")

        if st.button("🔁 Return to Quiz Creation"):
            reset_quiz()
            st.rerun()

def Swipe_Card():
    if "page2" not in st.session_state:
        st.session_state.page2 = "Swipe_Card"

    if st.session_state.page2 == "Swipe_Card":
        st.title("📝 Create a Cards")
        
        processed_files = st.session_state.namespaces or get_namespaces()
        
        for i in processed_files:
            container3 = st.container(border=True)
            row3 = container3.columns(spec=[5, 1],vertical_alignment="center")
            row3[0].write(f"Create Cards For {i} File")
            if row3[1].button("Generate",key=i):
                response=[]
                response=Generate_Card(i)
                if response[0]:
                    card_data=response[1]
                    st.session_state.card = card_data
                    st.session_state.page2 = "Cards"
                    st.rerun()
                else:
                    st.popover(response[0])

    elif st.session_state.page2 == "Cards":
        card = st.session_state.card
        if "next_btn" not in st.session_state:
            st.session_state.next_btn = False
        if "previous_btn" not in st.session_state:
            st.session_state.previous_btn = False
        if "card_index" not in st.session_state:
            st.session_state.card_index = 0

        def previous_card():
            if st.session_state.card_index > 0 :
                st.session_state.card_index -= 1
                st.session_state.next_btn = False
            else:
                st.session_state.previous_btn = True
        def next_card():
            if st.session_state.card_index < len(card)-1:
                st.session_state.card_index += 1
                st.session_state.previous_btn = False
            else:
                st.session_state.next_btn = True



        currnet_card = card[st.session_state.card_index]

        card_html=f'''

        <style>
            .card-container {{
              perspective: 1000px;
              width: 350px;
              height: 250px;
              margin: auto;    
            }}
            .card {{
              width: 100%;
              height: 100%;
              transition: transform 0.8s;
              transform-style: preserve-3d;
              position: relative;
              cursor: pointer;
            }}
            .card.flipped {{
              transform: rotateY(180deg);
            }}

            .card-side {{
              position: absolute;
              width: 100%;
              height: 100%;
              backface-visibility: hidden;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 24px;
              border: 1px solid white;  
              border-radius: 8px;
            }}
            .front {{
              padding:20px;
              background-color: transperent;
              color:white;
            }}

            .back {{
              padding:20px;
              background-color: transperent;
              font-size:20px;
              color:white;
              transform: rotateY(180deg);
            }}
        </style>

        <div class="card-container">
            <div class="card" id="flashcard" onclick="flipCard()">
                <div class="card-side front">{currnet_card['word']}</div>
                <div class="card-side back">{currnet_card['answer']}</div>
            </div>
        </div>
        <script>
            function flipCard() {{
                const card = document.getElementById('flashcard');
                card.classList.toggle('flipped');
            }}
        </script>
        '''
        html(card_html, height=400)
        btn = st.columns(spec=5,gap="small")
        if btn[1].button("<- Previous",disabled=st.session_state.previous_btn):
            previous_card()
            st.rerun()
        if btn[2].button("Next ->",disabled=st.session_state.next_btn):
            next_card()
            st.rerun()
        if btn[4].button("Back"):
            st.session_state.page2="Swipe_Card"
            st.rerun()


pg = st.navigation([Home,Upload_Metrial,Chat,Quizfy,Swipe_Card])
pg.run()