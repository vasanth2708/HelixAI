import React, { useState } from 'react';
import TopBar from '../components/TopBar';
import Sidebar from '../components/Sidebar';
import Chat from '../components/Chat';
import Workspace from '../components/Workspace';
import About from '../components/About';

// We accept all the props from App for chat data plus an optional `content` 
function MainLayout({
  user,
  handleLogout,
  loggedIn,
  sessions,
  activeSessionIndex,
  setActiveSessionIndex,
  createNewSession,
  chatLog,
  inputText,
  setInputText,
  sendMessage,
  sequence,
  handleEdit,
  saveEdits,
  content  // if set, we'll show that instead of chat/workspace
}) {
  // local state for toggle sidebar 
  // (you could pass the boolean from App if you want)
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div 
      style={{ 
        height: "100vh",
        display: "flex",
        flexDirection: "column"
      }}
    >
      {/* TopBar always shown in MainLayout */}
      <TopBar
        user={user}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        onLogout={handleLogout}
      />

      {/* Render either the About (or other content) OR the Chat/Workspace */}
      {content ? (
        // If we have a custom content, show it full width 
        // or however you like
        <div style={{ flex: 1 }}>
          {content}
        </div>
      ) : (
        // Otherwise, show the normal chat + workspace layout
        <div style={{ flex: 1, display: "flex" }}>
          <Sidebar
            sidebarOpen={sidebarOpen}
            sessions={sessions}
            activeSessionIndex={activeSessionIndex}
            setActiveSessionIndex={setActiveSessionIndex}
            createNewSession={createNewSession}
          />
          <Chat
            chatLog={chatLog}
            inputText={inputText}
            setInputText={setInputText}
            sendMessage={sendMessage}
          />
          <Workspace
            sequence={sequence}
            handleEdit={handleEdit}
            saveEdits={saveEdits}
          />
        </div>
      )}
    </div>
  );
}

export default MainLayout;
