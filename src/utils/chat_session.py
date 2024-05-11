from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


class GlobalChatHistory:
    def __init__(self):
        self.chat_histories = {}  # Dictionary to store history per session ID

    def initialize_message_history_chain(self, chain, session_id, chain_type):
        print("session_id: ", session_id)
        print("chain_type: ", chain_type)
        """Initializes or retrieves a chat memory chain for the given session ID."""
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = {
                chain_type: ChatMessageHistory()  # Create a nested dictionary
            }
        else:
            # Initialize the chain_type if it doesn't exist for the session
            self.chat_histories[session_id].setdefault(chain_type, ChatMessageHistory())

        print("self.chat_histories: ", self.chat_histories)
        return RunnableWithMessageHistory(
            chain,
            self.chat_histories[session_id][chain_type].messages,
            input_messages_key="input",
            output_messages_key="output",
            history_messages_key="chat_history",
        )


def handle_incoming_sms(db, chat_prompt, phone, global_chat_history, user_msg):
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

    if user_msg is None:
        return "Message missing, try resending your message again"

    intent = classify_intent(user_msg)
    session_id = db.get_session_id(phone)

    if intent == "scheduling":
        chain = chat_prompt.chain
    else:
        chain = chat_prompt.conversational_retrieval_chain

    if session_id is None:
        db.create_session(phone)
        session_id = db.get_session_id(phone)
        print("newly created session_id", session_id)
        message_history_chain = global_chat_history.initialize_message_history_chain(
            chain, session_id, intent
        )
    else:
        message_history_chain = global_chat_history.initialize_message_history_chain(
            chain, session_id, intent
        )
        print("session_id from previous session: ", session_id)
        db.write_last_session_accessed(session_id)

    return message_history_chain.invoke(
        {"input": user_msg}, {"configurable": {"session_id": session_id}}
    )


def classify_intent(msg):
    msg = msg.lower()  # Normalize for simpler matching
    if "schedule" in msg or "appointment" in msg:
        return "scheduling"
    else:
        return "general"
