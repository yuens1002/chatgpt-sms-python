from flask import Flask, request, g
from twilio.twiml.messaging_response import MessagingResponse
from prompt.chat_prompt_chain import ChatPrompt
from utils.chat_session import GlobalChatHistory, handle_incoming_sms
from utils.SQLite_setup import UserDb
from src.tools.zoho_booking_tools import ZohoCreateAppointment, ZohoCheckAvailability

create_appointment_tool = ZohoCreateAppointment()
check_availability_tool = ZohoCheckAvailability()

tools = [create_appointment_tool, check_availability_tool]

chat_prompt = ChatPrompt()
global_chat_history = GlobalChatHistory()

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = UserDb()
    return g.db


@app.route("/sms", methods=["POST"])
def sms_chat():
    """get incoming message"""
    print("request.form: ", request.form)
    inb_msg = request.form["Body"].lower()
    from_phone = request.form["From"]

    db = get_db()

    output = handle_incoming_sms(
        db, chat_prompt, from_phone, global_chat_history, inb_msg
    )

    # Start TwiML response
    resp = MessagingResponse()

    # write output to the message property
    resp.message(output)

    # Add a message
    # qa_res = pqa.query_store(v_store, inb_msg)
    # print(qa_res)
    # resp.message(qa_res)

    return str(resp)


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        del db  # Delete the db object, triggering the __del__ method


if __name__ == "__main__":
    app.run(debug=True)
