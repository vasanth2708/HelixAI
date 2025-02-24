import logging
from flask import Flask, g, request, jsonify
from database import engine, SessionLocal
from models import Base, User
from socketio_instance import socketio
from flask_cors import CORS
from config import Config

logging.basicConfig(level=logging.INFO)

def create_app():
    Base.metadata.create_all(bind=engine)
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'change_me'
    
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")
    
    @app.route("/")
    def index():
        return "Helix Multi-Agent Recruiting System is running."
    
    @app.route("/login", methods=["POST"])
    def login():
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        username = data.get("username")
        password = data.get("password")

        user = g.db.query(User).filter_by(username=username).first()
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        if user.password != password:
            return jsonify({"error": "Invalid password"}), 401
        
        return jsonify({
            "success": True,
            "user_id": user.id,
            "username": user.username
        }), 200
    
    @app.route("/signup", methods=["POST"])
    def signup():
        """A simple sign-up route to create a user in the DB."""
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "Missing username, email, or password"}), 400
        
        existing = g.db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            return jsonify({"error": "User with that name or email already exists"}), 409
        
        new_user = User(username=username, email=email, password=password)
        g.db.add(new_user)
        g.db.commit()
        
        return jsonify({
            "success": True,
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }), 201

    from utils.socket_events import handle_connect, handle_disconnect, handle_create_chat_session, \
        handle_load_chat_sessions, handle_load_chat_messages, handle_chat_message, \
        handle_edit_sequence, handle_save_sequence
    
    @app.before_request
    def create_session():
        g.db = SessionLocal()
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
    
    return app
    

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
