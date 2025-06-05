import streamlit as st
from langchain_community.vectorstores.azuresearch import AzureSearch
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title='ZENBOT', page_icon='🐰')
st.title("🤖ZENBOT")
st.caption("OUTLOOK 관련된 모든 것을 답해드립니다.")


def get_retriever():
    from langchain_openai import OpenAIEmbeddings
    embedding_model = OpenAIEmbeddings(model='text-embedding-3-large', openai_api_key=os.getenv('OPENAI_API_KEY'))
    vector_store = AzureSearch(azure_search_endpoint='https://dnasrh01.search.windows.net',
                                azure_search_key= '',
                                index_name='',
                                embedding_function=embedding_model.embed_query)
    return vector_store


def get_ai_message(user_message):
    from langchain_openai import ChatOpenAI
    from langchain.chains import RetrievalQA
    from langchain import hub

    vector_store = get_retriever()
    # Perform a similarity search
    docs = vector_store.similarity_search(
        query=user_message,
        search_type="similarity",
    )

    llm = ChatOpenAI(model='gpt-4o')
    prompt = hub.pull('rlm/rag-prompt')

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vector_store.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )

    ai_message = qa_chain({'query': user_message})
    return ai_message


if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message['role']):
        st.write(message['content'])

if user_question := st.chat_input(placeholder='OUTLOOK과 관련된 궁금한 내용들을 말씀해주세요!'):
    with st.chat_message('user'):
        st.write(user_question)
    st.session_state.message_list.append({'role': 'user', 'content': user_question})

    with st.spinner('답변을 생성하는 중입니다'):

        ai_response = get_ai_message(user_question)
        with st.chat_message('ZENBOT'):
            st.write(ai_response['result'])

        st.session_state.message_list.append({'role': 'ZENBOT', 'content': ai_response})
