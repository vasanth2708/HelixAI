from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import ChatSession, ChatMessage

chat_router = Blueprint("chat", __name__)

@chat_router.route("/sessions", methods=["POST"])
def create_session():
    data = request.json
    user_id = data.get("user_id")
    title = data.get("title", "Untitled Session")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    db = SessionLocal()
    try:
        new_session = ChatSession(user_id=user_id, title=title)
        db.add(new_session)
        db.commit()
        return jsonify({"message": "Session created", "session_id": new_session.id}), 201
    finally:
        db.close()