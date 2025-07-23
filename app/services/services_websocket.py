import asyncio
import json
from fastapi import WebSocket
from sqlalchemy.orm import Session
from uuid import UUID
from app.crud.crud_message import get_message
from app.crud.crud_message import update_bot_message_text
from app.services.services_chat import get_chat_service
from groq import Groq

client = Groq()

"""
Service operations for websocket connection.

Includes streaming llm response and building prompt to send to the llm.
"""
def llm_stream_sync(prompt: str):
    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        reasoning_format= "hidden",
    )
    for chunk in response:
        yield chunk.choices[0].delta.content or ""
        

async def stream_bot_response_service(
    websocket: WebSocket,
    db: Session,
    chat_id: UUID,
    message_id: UUID,
    prompt: str
) -> None:
    """
    stream the bots response. 

    Args:
        websocket: The websocket connection.
        db: The SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.
        message_id: The unique UUID for the message.
        prompt: the prompt to send the bot.

    Closes:
        Code=1000: Streaming complete.
        Code=1008: Message not found or unauthorized.

    Returns:
        None.
    """
    message = get_message(db, message_id)

    if not message or message.chat_id != chat_id:
        print("no message obj")
        await websocket.close(code=1008, reason="Message not found or unauthorized.")
        return

    for chunk in llm_stream_sync(prompt):
        msg = {"id": str(message_id), "sender": "bot", "text": chunk}
        await websocket.send_text(json.dumps(msg))

        # Step 2: Update DB incrementally
        update_bot_message_text(db, message, chunk)

    await websocket.close(code=1000, reason="Streaming complete.")


def build_prompt_service(
    db: Session,
    user_id: UUID,
    chat_id: UUID
) -> str:
    """
    Build a prompt to send the bot.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.
        chat_id: The unique UUID for the chat.
    
    Raises:
        None.

    Returns:
        The newly created prompt.
    """
    chat = get_chat_service(db, chat_id, user_id)
    messages = chat.messages if chat else []

    prompt_lines = []
    for message in messages:
        prompt_lines.append(f"{message.sender} : {message.text}")
    
    prompt = "\n".join(prompt_lines)

    return prompt
