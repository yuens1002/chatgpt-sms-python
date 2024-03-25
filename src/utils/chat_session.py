from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


class GlobalChatHistory:
    def __init__(self):
        self.chat_histories = {}  # Dictionary to store history per session ID

    def initialize_message_history_chain(self, chain, session_id):
        """Initializes or retrieves a chat memory chain for the given session ID."""
        self.chat_histories.setdefault(session_id, ChatMessageHistory())
        return RunnableWithMessageHistory(
            chain,
            self.chat_histories[session_id],
            input_messages_key="input",
            history_messages_key="chat_history",
        )


def handle_incoming_sms(db, phone, chain, global_chat_history, user_msg):
    # check if chat_history exists given a phone number
    # if not create one
    # create a new table entry in the chat_session table
    # initialize a chat history on the 'RunnableWithMessageHistory' instance using the session_id
    # invoke the chain with the user_msg and session_id
    # otherwise,

    # write to session's last_accessed property
    # write response to chat_history

    # invoke the chain with the user_msg and session_id
    # return the response

    session_id = db.get_session_id(phone)
    if session_id is None:
        db.create_session(phone)
        session_id = db.get_session_id(phone)
        message_history_chain = global_chat_history.initialize_message_history_chain(
            chain, session_id
        )
    else:
        message_history_chain = global_chat_history.initialize_message_history_chain(
            chain, session_id
        )
        db.write_last_session_accessed(session_id)

    return message_history_chain.invoke(
        {"input": user_msg}, {"configurable": {"session_id": session_id}}
    )
