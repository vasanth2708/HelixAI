from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Sequence
from agents.sequence_agent import generate_sequence
import json

sequence_router = Blueprint("sequence", __name__)

@sequence_router.route("/generate", methods=["POST"])
def generate_sequence_route():
    data = request.json
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    prompt = data.get("prompt")

    if not user_id or not session_id or not prompt:
        return jsonify({"error": "Missing required fields"}), 400

    db = SessionLocal()
    try:
        sequence_data = generate_sequence(prompt)

        new_sequence = Sequence(
            user_id=user_id,
            session_id=session_id,
            content=json.dumps(sequence_data)
        )
        db.add(new_sequence)
        db.commit()

        return jsonify({"message": "Sequence generated", "sequence": sequence_data}), 201
    finally:
        db.close()

@sequence_router.route("/edit", methods=["POST"])
def edit_sequence_route():
    data = request.json
    sequence_id = data.get("sequence_id")
    updated_content = data.get("content")

    if not sequence_id or not updated_content:
        return jsonify({"error": "Missing required fields"}), 400

    db = SessionLocal()
    try:

        sequence = db.query(Sequence).filter(Sequence.id == sequence_id).first()
        if not sequence:
            return jsonify({"error": "Sequence not found"}), 404

        sequence.content = json.dumps(updated_content)
        db.commit()

        return jsonify({"message": "Sequence updated", "sequence": updated_content}), 200
    finally:
        db.close()