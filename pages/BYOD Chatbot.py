__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import os
import utils
from utils import add_marcel_logo
import streamlit as st
from streaming import StreamHandler
from langchain.vectorstores import Chroma
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import UnstructuredCSVLoader
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import AzureOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="ChatPDF", page_icon="📄")
st.header('Chat with your documents')
st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.write('Has access to your uploaded documents and can respond to your queries by referring to the content within those documents')
add_marcel_logo()
class CustomDataChatbot:

    def __init__(self):
      
        os.environ["OPENAI_API_TYPE"] = st.secrets["OPENAI_API_TYPE"]
        os.environ["OPENAI_API_BASE"] = st.secrets["OPENAI_API_BASE"]
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        os.environ["OPENAI_API_VERSION"] = st.secrets["OPENAI_API_VERSION"]
        #utils.configure_openai_api_key()
        st.write(sys.version)
        self.openai_model = "gpt-35-turbo"

    def save_file(self, file):
        folder = 'tmp'
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_path = f'./{folder}/{file.name}'
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
        return file_path

    @st.spinner('Analyzing documents..')
    def setup_qa_chain(self, uploaded_files):
        # Load documents
        docs = []
        for file in uploaded_files:
            file_path = self.save_file(file)
            file_extension = os.path.splitext(file_path)
            if file_extension == 'csv':
                loader = UnstructuredCSVLoader(file_path)
            elif file_extension == 'ppt':
                loader = UnstructuredPowerPointLoader(file_path)
            elif file_extension = 'docx':
                loader = UnstructuredWordDocumentLoader(file_path)
            else :
                loader = UnstructuredFileLoader(file_path)
          
            docs.extend(loader.load())
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # Create embeddings and store in vectordb
        embeddings = OpenAIEmbeddings(chunk_size=1)
       # vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)
        vectordb = Chroma.from_documents(splits, embeddings)

        # Define retriever
        retriever = vectordb.as_retriever()

        # Setup memory for contextual conversation        
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )

        # Setup LLM and QA chain
        llm = AzureOpenAI( deployment_name="gpt-35-turbo",model_name=self.openai_model, temperature=0, streaming=True)
        qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory, verbose=True)
        return qa_chain

    @utils.enable_chat_history
    def main(self):

        # User Inputs
        uploaded_files = st.sidebar.file_uploader(label='Upload your files', accept_multiple_files=True)
        if not uploaded_files:
            st.error("Please upload your documents to continue!")
            st.stop()

        user_query = st.chat_input(placeholder="Ask me anything!")

        if uploaded_files and user_query:
            qa_chain = self.setup_qa_chain(uploaded_files)

            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                response = qa_chain.run(user_query, callbacks=[st_cb])
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()