import logging
import json
import re
from flask import request, copy_current_request_context
from flask_socketio import emit
from agents.chat_agent import question_agents
from agents.sequence_agent import generate_new_sequence, add_additional_step_with_detail, edit_step_with_llm
from utils.memory import store_conversation_embedding
from database import SessionLocal
from models import Sequence, ChatSession, ChatMessage, User
from socketio_instance import socketio
import asyncio

logger = logging.getLogger(__name__)

USER_SESSIONS = {}

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    USER_SESSIONS[request.sid] = {
        "conversation_history": [],
        "collected_data": {},
        "sequence": [],
        "awaiting_details": False,
    }
    emit('connection_response', {'message': 'Connected to Helix recruiting AI!'})
    emit("chat_response", {"sender": "System", "text": "How can I help?"})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")
    USER_SESSIONS.pop(request.sid, None)

@socketio.on('create_chat_session')
def handle_create_chat_session(data):
    @copy_current_request_context
    def _create_chat_session():
        logger.info("Creating new chat session with data: %s", data)
        db_session = SessionLocal()
        try:
            user_id = data.get("user_id")
            title = data.get("title", "Untitled Chat")
            new_session = ChatSession(user_id=user_id, session_title=title)
            db_session.add(new_session)
            db_session.commit()
            db_session.refresh(new_session)
            logger.info("New session created: %s", new_session.id)
            USER_SESSIONS[request.sid] = {
                "user_id": user_id,
                "conversation_history": [],
                "collected_data": {},
                "sequence": [],
                "awaiting_details": False,
            }
            emit("new_chat_session", {"session_id": new_session.id, "session_title": new_session.session_title}, room=request.sid)
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error creating chat session: {e}")
            emit("new_chat_session", {"error": str(e)}, room=request.sid)
        finally:
            db_session.close()
    _create_chat_session()


@socketio.on('load_chat_sessions')
def handle_load_chat_sessions(data):
    @copy_current_request_context
    def _load_chat_sessions():
        db_session = SessionLocal()
        try:
            user_id = data.get("user_id")
            sessions = db_session.query(ChatSession).filter_by(user_id=user_id).all()
            result = [{"session_id": s.id, "session_title": s.session_title, "created_at": str(s.created_at) if s.created_at else None} for s in sessions]
            emit("chat_sessions_response", result, room=request.sid)
        except Exception as e:
            logger.error(f"Error loading chat sessions: {e}")
            emit("chat_sessions_response", {"error": str(e)}, room=request.sid)
        finally:
            db_session.close()
    _load_chat_sessions()

@socketio.on('load_chat_messages')
def handle_load_chat_messages(data):
    @copy_current_request_context
    def _load_chat_messages():
        db_session = SessionLocal()
        try:
            session_id = data.get("session_id")
            messages = db_session.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
            logger.info(f"Retrieved {len(messages)} messages for session_id {session_id}")
            msg_list = [{"id": m.id, "sender": m.sender, "text": m.text, "timestamp": str(m.timestamp)} for m in messages]
            emit("chat_messages_response", {"session_id": session_id, "messages": msg_list}, room=request.sid)
        except Exception as e:
            logger.error(f"Error loading chat messages: {e}")
            emit("chat_messages_response", {"error": str(e)}, room=request.sid)
        finally:
            db_session.close()
    _load_chat_messages()



@socketio.on('chat_message')
def handle_chat_message(data):
    @copy_current_request_context
    def _handle_chat_message():
        user_session = USER_SESSIONS.get(request.sid, {
            "conversation_history": [],
            "collected_data": {},
            "sequence": [],
            "awaiting_details": False,
        })
        user_msg = data.get("message", "").strip()
        session_id = data.get("session_id")
        if not user_msg:
            emit("chat_response", {"error": "No message provided."}, room=request.sid)
            return

        db_session = SessionLocal()
        try:
            new_msg = ChatMessage(session_id=session_id, sender="User", text=user_msg)
            db_session.add(new_msg)
            db_session.commit()

            store_user_message(session_id, user_msg)

            user_session["conversation_history"].append({"sender": "User", "text": user_msg})

            full_conversation = "\n".join(f"{m['sender']}: {m['text']}" for m in user_session["conversation_history"])
            store_conversation_embedding(session_id, full_conversation)

            agent_reply = question_agents(user_session["conversation_history"], user_session["collected_data"], session_id=session_id)
            upper_reply = agent_reply.strip().upper()

            if upper_reply == "DONE":
                emit("chat_response", {"sender": "Helix", "text": "Generating sequence..."}, room=request.sid)
                store_agent_message(session_id, "Generating sequence...")
                
                summary_text = "\n".join(f"{m['sender']}: {m['text']}" for m in user_session["conversation_history"])
                user_session["collected_data"] = {"conversation": summary_text}
                new_seq_data = generate_new_sequence(user_session["collected_data"])
                user_session["sequence"] = new_seq_data.get("sequence", [])
                user_session["awaiting_details"] = False
                
                agent_text = "Sequence updated."
                user_session["conversation_history"].append({"sender": "Helix", "text": agent_text})
                emit("chat_response", {"sender": "Helix", "text": agent_text}, room=request.sid)
                store_agent_message(session_id, agent_text)
                
                store_sequence_to_db(user_session.get("user_id"), new_seq_data)
                emit("chat_response", {"sequence": user_session["sequence"]}, room=request.sid)

            elif upper_reply == "ADD_STEP":
                agent_text = "Adding new step..."
                emit("chat_response", {"sender": "Helix", "text": agent_text}, room=request.sid)
                store_agent_message(session_id, agent_text)
                
                additional_detail = user_msg
                new_step_data = add_additional_step_with_detail(user_session["sequence"], additional_detail)
                new_steps = new_step_data.get("sequence", [])
                if new_steps:
                    user_session["sequence"].append(new_steps[0])
                
                agent_text = "Sequence updated with additional step."
                user_session["conversation_history"].append({"sender": "Helix", "text": agent_text})
                emit("chat_response", {"sender": "Helix", "text": agent_text}, room=request.sid)
                store_agent_message(session_id, agent_text)
                
                store_sequence_to_db(user_session.get("user_id"), {"sequence": user_session["sequence"]})
                emit("chat_response", {"sequence": user_session["sequence"]}, room=request.sid)

            elif upper_reply == "EDIT_STEP":
                new_seq_data = edit_step_with_llm(user_session["sequence"], user_msg)
                if new_seq_data and "sequence" in new_seq_data:
                    user_session["sequence"] = new_seq_data["sequence"]
                    agent_text = "Step updated."
                    user_session["conversation_history"].append({"sender": "Helix", "text": agent_text})
                    emit("chat_response", {"sender": "Helix", "text": agent_text}, room=request.sid)
                    store_agent_message(session_id, agent_text)
                    
                    store_sequence_to_db(user_session.get("user_id"), {"sequence": user_session["sequence"]})
                    emit("chat_response", {"sequence": user_session["sequence"]}, room=request.sid)
                else:
                    emit("chat_response", {"sender": "Helix", "text": "Unable to update step. Please try again."}, room=request.sid)
            else:
                user_session["conversation_history"].append({"sender": "Helix", "text": agent_reply})
                emit("chat_response", {"sender": "Helix", "text": agent_reply}, room=request.sid)
                store_agent_message(session_id, agent_reply)

            USER_SESSIONS[request.sid] = user_session

        except Exception as e:
            db_session.rollback()
            logger.error(f"Error handling chat message: {e}")
            emit("chat_response", {"error": str(e)}, room=request.sid)
        finally:
            db_session.close()
    _handle_chat_message()



def store_user_message(session_id: str, message: str):
    db_session = SessionLocal()
    try:
        user_msg = ChatMessage(session_id=session_id, sender="User", text=message)
        db_session.add(user_msg)
        db_session.commit()
    except Exception as e:
        logger.error(f"Error storing user message: {e}")
        db_session.rollback()
    finally:
        db_session.close()

def store_agent_message(session_id: str, message: str):
    db_session = SessionLocal()
    try:
        agent_msg = ChatMessage(session_id=session_id, sender="Helix", text=message)
        db_session.add(agent_msg)
        db_session.commit()
    except Exception as e:
        logger.error(f"Error storing agent message: {e}")
        db_session.rollback()
    finally:
        db_session.close()

def store_sequence_to_db(user_id: int, sequence_content: dict):
    """Persist the generated sequence into the database."""
    db_session = SessionLocal()
    try:
        seq = Sequence(user_id=user_id, content=json.dumps(sequence_content))
        db_session.add(seq)
        db_session.commit()
        logger.info("Sequence stored in DB.")
    except Exception as e:
        logger.error(f"Error storing sequence to DB: {e}")
        db_session.rollback()
    finally:
        db_session.close()


@socketio.on('edit_sequence')
def handle_edit_sequence(data):
    @copy_current_request_context
    def _handle_edit_sequence():
        user_session = USER_SESSIONS.get(request.sid, {})
        new_seq = data.get("sequence", [])
        user_session["sequence"] = new_seq
        USER_SESSIONS[request.sid] = user_session
        emit("edit_response", {"sequence": new_seq}, room=request.sid)
    _handle_edit_sequence()

@socketio.on('save_sequence')
def handle_save_sequence(data):
    @copy_current_request_context
    def _handle_save_sequence():
        emit("save_response", {"status": "ok", "message": "Sequence saved to DB (mock)."}, room=request.sid)
    _handle_save_sequence()
