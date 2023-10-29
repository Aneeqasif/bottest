########################################################
                #streamlit app#
########################################################


import dataclasses
import streamlit as st
import openai
import os
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def solarpdfllm(context:str, chat_history:str, human_input):
    final_response=openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
        {"role": "system", "content": """you are a helpful chatbot who needs to answer
         questions about Entanglement in Coupled Cavity Magnomechanics i have given you
         a detailed manual about it.
"""},
        {"role": "user", "content": f"""
    CONTEXT: {context}
    You are a helpful assistant, above is some context, 
    Please answer the question, and make sure you follow ALL of the rules below:
    1. Answer the questions only based on context provided, do not make things up
    2. Answer questions in a helpful manner that straight to the point, with clear structure & all relevant information that might help users answer the question
    3. Anwser should be formatted in Markdown
    4. If there are relevant tables or markdown images they are very important reference data, please include them as is as part of the answer and use standard markdown syntax when you have to refer to a image and try to include as many images as possible in all answers.

    {chat_history}
    Human: {human_input}
    ANSWER (formatted in Markdown):
"""}
        ],
        temperature=0,
        stream=False
    )
    return final_response["choices"][0]["message"]["content"]



@dataclasses.dataclass
class UserConversation:
    conversation: list[str] = dataclasses.field(default_factory=list)

    def add_to_conversation(self, message: str):
        self.conversation.append(message)
    # write list as string but with alternating lines as user and AI


    def write_as_string(self, num_lines=5):
        start_index = 0
        if len(self.conversation) > num_lines:
            start_index = len(self.conversation) - num_lines
        # join the lines together with a newline character between them
        return "\n".join(self.conversation[start_index:])
    
def get_retrievals(query):
    
    retrieved_docs = retriever.get_relevant_documents(query)
    docs=""
    for doc in retrieved_docs:
        docs=docs+doc.page_content+"\n\n"

    return docs



if not hasattr(st.session_state, 'coversation'):
    new_conversation = UserConversation()
    st.session_state.conversation = new_conversation
else:
    new_conversation = st.session_state.conversation

if not hasattr(st.session_state, 'retriever'):
    from retriever import retriever
    st.session_state.retriever = retriever
else:
    retriever = st.session_state.retriever

#retrieved_docs = retriever.get_relevant_documents("how to use instruction panel")

#chain({"input_documents": retrieved_docs, "human_input": "can you tell me how to use
        #instruction panel, hopefullu with some images"}, return_only_outputs=True)




st.title("Dilawaiz api thesis")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    new_conversation.add_to_conversation(f"human:prompt")
    response=solarpdfllm(get_retrievals(prompt), new_conversation.write_as_string(), prompt)
    new_conversation.add_to_conversation(f"assistant:{response}")
    st.session_state.conversation = new_conversation
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
