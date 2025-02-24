import React from 'react';

function TopBar({ user, onLogout, onToggleSidebar }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      borderBottom: '2px solid #d11a2a',
      padding: '0.5rem',
      backgroundColor: '#fff'
    }}>
      {/* Toggle sidebar */}
      <button
        onClick={onToggleSidebar}
        style={{
          marginRight: '1rem',
          padding: '0.5rem',
          backgroundColor: '#d11a2a',
          color: '#fff',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '14px'
        }}
      >
        Toggle Sidebar
      </button>

      <h2 style={{ margin: 0, color: '#d11a2a' }}>Chat</h2>

      {/* Push remainder to the right */}
      <div style={{ flex: 1 }} />

      {user && (
        <div style={{ marginRight: '1rem', color: '#555' }}>
          Logged in as <strong>{user.username}</strong>
        </div>
      )}
      <button
        onClick={onLogout}
        style={{
          padding: '0.5rem 1rem',
          backgroundColor: 'gray',
          color: '#fff',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '14px'
        }}
      >
        Logout
      </button>
    </div>
  );
}

export default TopBar;
