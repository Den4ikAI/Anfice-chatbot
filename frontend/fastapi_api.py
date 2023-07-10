from fastapi import FastAPI, Request
import uvicorn
from bot.core import CoreSession
from config.config import access_tokens
from pydantic import BaseModel

app = FastAPI()
sess = CoreSession()


class UserMessage(BaseModel):
    token: str
    user_id: int
    message: str


class BotMessage(BaseModel):
    token: str
    user_id: int
    message: str


class SystemPrompt(BaseModel):
    token: str
    user_id: int
    prompt: str


class ProcessUserMessage(BaseModel):
    token: str
    user_id: int


class Command(BaseModel):
    token: str
    user_id: str


@app.post("/process_user_message")
def process_user_message(user_data: ProcessUserMessage):
    if user_data.token in access_tokens:
        answer = sess.process_user_message(user_data.user_id)
        return {"message": answer}
    else:
        return {"message": "Invalid token"}


@app.post('/add_user_message')
def add_user_message(user_data: UserMessage):
    if user_data.token in access_tokens:
        sess.add_user_message(user_data.user_id, user_data.message)
        return {"message": "Message added"}
    else:
        return {"message": "Invalid token"}


@app.post('/add_bot_message')
def add_bot_message(bot_data: BotMessage):
    if bot_data.token in access_tokens:
        sess.add_bot_message(bot_data.user_id, bot_data.message)
        return {"message": "Message added"}
    else:
        return {"message": "Invalid token"}


@app.post("/set_system_prompt")
def set_system_prompt(prompt_data: SystemPrompt):
    if prompt_data.token in access_tokens:
        sess.set_system_prompt(prompt_data.user_id, prompt_data.prompt)
        return {"message": "Prompt processed successfully"}
    else:
        return {"message": "Invalid token"}


@app.get("/get_last_bot_message")
def get_answer(user_data: Command):
    if user_data.token in access_tokens:
        bot_message = sess.get_last_bot_message(user_data.user_id)
        return {'message': bot_message}
    else:
        return {"message": "Invalid token"}


@app.get("/get_last_user_message")
def get_last_user_message(user_data: Command):
    if user_data.token in access_tokens:
        user_message = sess.get_last_user_message(user_data.user_id)
        return {'message': user_message}
    else:
        return {"message": "Invalid token"}


@app.get("/clear_context")
def clear_context(user_data: Command):
    if user_data.token in access_tokens:
        sess.clear_context(user_data.user_id)
        return {"message": "Context deleted!"}
    else:
        return {"message": "Invalid token"}


@app.get("/get_dialog")
def get_dialog(user_data: Command):
    if user_data.token in access_tokens:
        dialog = sess.get_dialog(user_data.user_id)
        return {"message": dialog}
    else:
        return {"message": "Invalid token"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
