import React from 'react';

function About() {
  return (
    <div style={{
      display: 'flex',
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div>
        <h1>About This App</h1>
        <p>A React + Socket.IO demo with routes for Login, Home, and About.</p>
      </div>
    </div>
  );
}

export default About;
