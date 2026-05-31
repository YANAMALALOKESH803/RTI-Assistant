import os

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st
from transformers import pipeline

# ---------------- PAGE CONFIG ----------------

st.set_page_config(page_title="RTI Assistant AI", page_icon="⚖️", layout="wide")

# ---------------- LOAD CSS ----------------

with open("assets/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- TITLE ----------------

st.markdown(
    """
    <div class='main-title'>
    RTI Assistant AI
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='subtitle'>
    AI Civic Rights Assistant for India
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- SIDEBAR ----------------

st.sidebar.title("⚡ RTI Assistant")

st.sidebar.markdown("### Suggested Questions")

questions = ["How to file RTI?", "What is RTI fee?", "Appeal process?", "RTI response time?"]

selected_question = ""

for q in questions:
    if st.sidebar.button(q):
        selected_question = q

st.sidebar.markdown("---")
st.sidebar.markdown("### Features")

st.sidebar.success("AI Answers")
st.sidebar.success("RTI Draft Generator")
st.sidebar.success("Sources Included")
st.sidebar.success("Citizen Friendly")

# ---------------- LOAD DATABASE ----------------


@st.cache_resource
def load_db():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

    return vector_db


# ---------------- LOAD MODEL ----------------


@st.cache_resource
def load_model():
    return pipeline("text-generation", model="gpt2")


db = load_db()
generator = load_model()

# ---------------- HISTORY ----------------

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- INPUT ----------------

query = st.text_input("Ask your RTI Question", value=selected_question)

# ---------------- PROCESS QUERY ----------------

if query:
    with st.spinner("AI is thinking..."):
        docs = db.similarity_search(query, k=3)

        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""
Context:
{context}

Question:
{query}

Answer:
"""

        result = generator(prompt, max_new_tokens=100)

        answer = result[0]["generated_text"]

        st.session_state.history.append({"question": query, "answer": answer, "docs": docs})

# ---------------- DISPLAY CHAT ----------------

for idx, item in enumerate(st.session_state.history):
    st.markdown(
        f"""
        <div class="chat-user">
        <b>You</b><br><br>
        {item["question"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="chat-ai">
        <b>AI Assistant</b><br><br>
        {item["answer"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📄 Sources Used"):
        for i, doc in enumerate(item["docs"]):
            source = doc.metadata.get("source", "Unknown")

            st.write(os.path.basename(source))

            if os.path.exists(source):
                with open(source, "rb") as pdf_file:
                    st.download_button(
                        label=f"Open {os.path.basename(source)}",
                        data=pdf_file,
                        file_name=os.path.basename(source),
                        mime="application/pdf",
                        key=f"pdf_{idx}_{i}",
                    )

st.divider()

# ---------------- DRAFT GENERATOR ----------------

st.subheader("RTI Draft Generator")

issue = st.text_area("Describe your issue")

if st.button("Generate Draft"):
    draft = f"""
To,
Public Information Officer

Subject: RTI Request

Under Section 6(1) of the RTI Act,
I request information regarding:

{issue}

Kindly provide the requested information.

Regards
"""

    st.text_area("Generated RTI Draft", draft, height=250)

    st.download_button("Download Draft", draft, file_name="RTI_Draft.txt", key="draft_download")
