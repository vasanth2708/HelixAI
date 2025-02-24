import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { io } from 'socket.io-client';

import Login from './components/Login';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import Workspace from './components/Workspace';

function App() {
  const [loggedIn, setLoggedIn] = useState(localStorage.getItem('loggedIn') === 'true');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')));
  const [socket, setSocket] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sequence, setSequence] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    if (loggedIn && user) {
      const newSocket = io("http://localhost:8000", { transports: ["websocket"] });
      setSocket(newSocket);

      newSocket.on("connect", () => {
        console.log("[socket] connected");
        newSocket.emit("load_chat_sessions", { user_id: user.user_id });
      });

      newSocket.on("connection_response", (data) => {
        console.log("[socket] connection_response:", data);
      });

      newSocket.on("chat_sessions_response", (data) => {
        if (Array.isArray(data)) {
          setSessions(data);
          localStorage.setItem('sessions', JSON.stringify(data));
        } else {
          console.error("Error in chat_sessions_response:", data);
        }
      });

      newSocket.on("chat_messages_response", (payload) => {
        if (activeSession && payload.session_id === activeSession.session_id) {
          setMessages(payload.messages);
          localStorage.setItem(`messages_${activeSession.session_id}`, JSON.stringify(payload.messages));
        }
      });

      newSocket.on("chat_response", (data) => {
        console.log("[socket] chat_response:", data);
        if (activeSession && data.sender && data.text) {
          setMessages((prev) => [
            ...prev,
            { sender: data.sender === "System" ? "Helix" : data.sender, text: data.text },
          ]);
          localStorage.setItem(
            `messages_${activeSession.session_id}`,
            JSON.stringify([
              ...messages,
              { sender: data.sender === "System" ? "Helix" : data.sender, text: data.text },
            ])
          );
        }
        if (data.sequence) {
          setSequence(data.sequence);
          localStorage.setItem(`sequence_${activeSession.session_id}`, JSON.stringify(data.sequence));
        }
      });

      newSocket.on("edit_response", (data) => {
        console.log("[socket] edit_response:", data);
        if (data.sequence) {
          setSequence(data.sequence);
          localStorage.setItem(`sequence_${activeSession.session_id}`, JSON.stringify(data.sequence));
        }
      });

      newSocket.on("new_session_created", (newSession) => {
        setSessions((prev) => [...prev, newSession]);
        localStorage.setItem('sessions', JSON.stringify([...sessions, newSession]));
        setActiveSession(newSession); // Set the new session as active
      });

      return () => {
        newSocket.disconnect();
      };
    }
  }, [loggedIn, user, activeSession]);

  useEffect(() => {
    const savedSessions = JSON.parse(localStorage.getItem('sessions'));
    if (savedSessions) {
      setSessions(savedSessions);
    }
  }, []);

  const createNewChat = () => {
    if (socket && user) {
      socket.emit("create_chat_session", { user_id: user.user_id });
    }
  };

  const loadMessages = (sessionObj) => {
    setActiveSession(sessionObj);
    const savedMessages = JSON.parse(localStorage.getItem(`messages_${sessionObj.session_id}`));
    const savedSequence = JSON.parse(localStorage.getItem(`sequence_${sessionObj.session_id}`));
    setMessages(savedMessages || []);
    setSequence(savedSequence || []);
    if (socket) {
      socket.emit("load_chat_messages", { session_id: sessionObj.session_id });
    }
  };

  const sendMessage = (text) => {
    if (!activeSession || !socket) return;
    setMessages((prev) => [...prev, { sender: "User", text }]);
    localStorage.setItem(
      `messages_${activeSession.session_id}`,
      JSON.stringify([...messages, { sender: "User", text }])
    );
    socket.emit("chat_message", {
      session_id: activeSession.session_id,
      user_id: user.user_id,
      message: text,
    });
  };

  const handleEdit = (index, newText) => {
    const updated = [...sequence];
    updated[index].message = newText;
    setSequence(updated);
    localStorage.setItem(`sequence_${activeSession.session_id}`, JSON.stringify(updated));
  };

  const saveEdits = () => {
    if (!socket) return;
    socket.emit("edit_sequence", { sequence });
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setUser(null);
    setSessions([]);
    setActiveSession(null);
    setMessages([]);
    setSequence([]);
    localStorage.clear();
    navigate("/login");
  };

  return (
    <Routes>
      <Route
        path="/login"
        element={
          loggedIn 
            ? <Navigate to="/home" replace /> 
            : (
              <Login 
                onLogin={(u) => {
                  setUser(u);
                  setLoggedIn(true);
                  localStorage.setItem('loggedIn', 'true');
                  localStorage.setItem('user', JSON.stringify(u));
                  navigate("/home");
                }} 
              />
            )
        }
      />
      <Route
        path="/home"
        element={
          !loggedIn 
            ? <Navigate to="/login" replace />
            : (
              <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
                <TopBar 
                  user={user}
                  onLogout={handleLogout}
                  onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                />
                <div style={{ flex: 1, display: "flex" }}>
                  <Sidebar
                    sidebarOpen={sidebarOpen}
                    sessions={sessions}
                    createNewChat={createNewChat}
                    loadMessages={loadMessages}
                  />
                  <Chat
                    activeSession={activeSession}
                    messages={messages}
                    sendMessage={sendMessage}
                  />
                  <Workspace
                    sequence={sequence}
                    handleEdit={handleEdit}
                    saveEdits={saveEdits}
                  />
                </div>
              </div>
            )
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;