import React from 'react';

function Sidebar({ sidebarOpen, sessions, createNewChat, loadMessages }) {
  return (
    <div 
      style={{
        width: sidebarOpen ? "200px" : "0",
        transition: "width 0.3s ease",
        overflow: "hidden",
        backgroundColor: "#f9f9f9",
        borderRight: "1px solid #ccc",
        display: "flex",
        flexDirection: "column"
      }}
    >
      {sidebarOpen && (
        <div 
          style={{ 
            padding: "1rem", 
            borderBottom: "1px solid #ccc", 
            backgroundColor: "#fff"
          }}
        >
          <button
            onClick={createNewChat}
            style={{
              width: "100%",
              padding: "0.5rem",
              backgroundColor: "#d11a2a",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px"
            }}
          >
            + New Chat
          </button>
        </div>
      )}

      {sidebarOpen && (
        <div style={{ flex: 1, overflowY: "auto" }}>
          {sessions.length === 0 ? (
            <div style={{ padding: "1rem", color: "#777" }}>
              No previous chats. Start a new one!
            </div>
          ) : (
            sessions.map((s) => (
              <div
                key={s.session_id}
                onClick={() => loadMessages(s)}
                style={{
                  padding: "0.75rem 1rem",
                  cursor: "pointer",
                  borderBottom: "1px solid #ccc",
                  backgroundColor: "#fff",
                  margin: "0.25rem",
                  borderRadius: "4px",
                  boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)"
                }}
              >
                {s.session_title || `Chat ${s.session_id}`}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default Sidebar;