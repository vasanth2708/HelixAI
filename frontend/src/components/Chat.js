import React, { useState } from 'react';

function Chat({ activeSession, messages, sendMessage }) {
  const [inputText, setInputText] = useState("");

  if (!activeSession) {
    return (
      <div style={{
        width: "300px",
        borderRight: "1px solid #ccc",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#f9f9f9"
      }}>
        <div style={{ padding: "1rem" }}>
          <p style={{ color: "#666" }}>Select or create a chat session to begin.</p>
        </div>
      </div>
    );
  }

  const handleSend = () => {
    if (!inputText.trim()) return;
    sendMessage(inputText);
    setInputText("");
  };

  return (
    <div 
      style={{
        width: "300px",
        display: "flex",
        flexDirection: "column",
        borderRight: "1px solid #ccc",
        backgroundColor: "#f9f9f9"
      }}
    >
      <div style={{
        flex: 1,
        overflowY: "auto",
        padding: "1rem",
        backgroundColor: "#fff"
      }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              marginBottom: "1rem",
              padding: "0.5rem",
              backgroundColor: msg.sender === 'Helix' ? '#e9f5ff' : '#f1f1f1',
              borderRadius: '8px',
              border: msg.sender === 'Helix' ? '1px solid #d1e8ff' : '1px solid #ddd'
            }}
          >
            <strong style={{ color: msg.sender === 'How can I help you?' ? '#007bff' : '#333' }}>
              {msg.sender}:
            </strong> {msg.text}
          </div>
        ))}
      </div>

      <div style={{
        padding: "1rem",
        borderTop: "1px solid #eee",
        backgroundColor: "#fff"
      }}>
        <textarea
          style={{
            width: "100%",
            marginBottom: "0.5rem",
            padding: "0.75rem 0 0.75rem 0.75rem",
            border: "1px solid #ddd",
            borderRadius: "4px",
            fontSize: "14px",
            resize: "vertical", 
            minHeight: "40px", 
            maxHeight: "150px", 
            overflowY: "auto", 
          }}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type your message..."
          rows={1} 
        />
        <button
          onClick={handleSend}
          style={{
            width: "100%",
            padding: "0.75rem",
            backgroundColor: "#d11a2a",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;