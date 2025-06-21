# 📚 Fast Study

**Fast Study** is an intelligent learning assistant built with Streamlit that helps users understand large documents faster by combining **PDF parsing**, **vector embeddings**, **Pinecone search**, and **LLM-based interaction**. It’s designed for students, researchers, and professionals who want to transform their study materials into **interactive chat, quizzes, and flashcards**.

---

## 🚀 Project Overview

Traditional studying from large PDFs is inefficient. Fast Study solves this by:

- Converting your uploaded PDFs into searchable **vector embeddings**.
- Enabling **chat-based Q&A** from your content using Retrieval-Augmented Generation (RAG).
- Creating **custom quizzes** to test understanding.
- Generating **swipeable flashcards** for revision.

---

### 🏠 Home Page

Introduces the Fast Study application:
- Explains how the system works.
- Provides a quick overview of features.
- Acts as the landing page for user onboarding.

📷 ![Home Page](https://github.com/user-attachments/assets/797f2389-f7fe-477e-bae0-b3fa93c81ad0)


---

### 📤 Upload File Page

Allows users to upload PDF documents. This page:
- Extracts text from uploaded files.
- Breaks content into chunks.
- Converts chunks into **vector embeddings** using a model `SentenceTransformers` And `GoogleGenerativeAIEmbeddings`.
- Stores embeddings into **Pinecone**, a fast and scalable vector database.

 ![Upload Page](https://github.com/user-attachments/assets/3e783da1-1f9b-41a7-a10f-94cfb6d42de1)



---

### 💬 Chat Page

Chat with your own content!

- Asks user queries about the uploaded PDFs.
- Performs semantic similarity search in Pinecone to retrieve relevant chunks.
- Combines the context with the query to generate answers using an LLM ( Gemini-flash-2.0).
- Responses feel like chatting with a subject-matter expert trained on your PDFs.

 ![Chat Page](https://github.com/user-attachments/assets/944cd41c-3e10-4d1a-97eb-009615a8492d)


---

### ❓ Quizy Page

Turn study material into an interactive quiz.

- Automatically generates multiple-choice questions based on uploaded content.
- Shows one question at a time with options to:
  - **Flip answers**
  - **Navigate** with Previous/Next
  - **Submit** and get results (score, attempted, correct).
- Great for self-assessment and revision.

 ![Quiz Generate](https://github.com/user-attachments/assets/b1ed1257-78c1-4bbc-875b-15cfc86033a4)
 
 ![Quiz Page](https://github.com/user-attachments/assets/02306bdb-9bc0-4e47-ba77-514b7961087a)



---

### 🔄 Swipe_Card Page

Like digital flashcards to reinforce memory.

- Extracts important keywords, definitions, or full forms from content.
- Displays each as a **flippable card**: front (term) → back (definition).
- After flipping, user can **swipe to the next card**.
- Fun and engaging way to study key concepts!

 ![Swipe Card Page](https://github.com/user-attachments/assets/c0cc9a11-d682-4710-8fa0-053b5918e478)
 
![Card Demo](https://github.com/user-attachments/assets/99e43ee6-5807-4dfd-87e4-e5528fb39801)

---

## 📊 RAG Pipeline – How It Works

Fast Study uses a **Retrieval-Augmented Generation** approach.

> 📌 Diagram below explains the full flow:

![RAG Pipeline]


### Steps:
1. **PDF Upload**: User uploads study material in PDF format.
2. **Text Extraction**: PDF text is extracted and chunked into sections.
3. **Vectorization**: Each chunk is transformed into a numerical embedding.
4. **Storage**: Embeddings are stored in Pinecone for fast retrieval.
5. **User Query**: User types a question.
6. **Retriever**: Finds the top-matching chunks by comparing vector similarity.
7. **LLM Input**: Query + matched chunks are sent to an LLM (e.g., GPT).
8. **Answer**: The LLM provides a natural language response to the user.

---

## 📦 Tech Stack

| Layer        | Tools Used                               |
|--------------|------------------------------------------|
| Frontend     | Streamlit                                |
| Embeddings   | GoogleGenerativeAIEmbeddings             |
| Vector DB    | Pinecone                                 |
| Backend Logic| Python, Langchain                        |
| PDF Parsing  | PyPDFLoader                              |

---

