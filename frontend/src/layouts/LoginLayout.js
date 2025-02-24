import React from 'react';

function LoginLayout({ children }) {
  return (
    <div 
      style={{ 
        height: "100vh",
        display: "flex", 
        flexDirection: "column",
        // The difference is we do NOT show top bar here
      }}
    >
      {children}
    </div>
  );
}

export default LoginLayout;
