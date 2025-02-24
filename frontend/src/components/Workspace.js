import React, { useState, useEffect, useRef } from 'react';

const Workspace = ({ sequence, handleEdit, saveEdits }) => {
  const textareaRefs = useRef([]);

  // Function to adjust textarea height based on content
  const adjustTextareaHeight = (textarea) => {
    if (textarea) {
      textarea.style.height = 'auto'; // Reset height
      textarea.style.height = `${textarea.scrollHeight}px`; // Set height based on content
    }
  };

  // Adjust textarea heights when sequence changes
  useEffect(() => {
    textareaRefs.current.forEach(adjustTextareaHeight);
  }, [sequence]);

  return (
    <div style={{ 
      flex: 1, 
      padding: "1rem", 
      backgroundColor: "#fff",
      borderLeft: "1px solid #ccc",
      overflowY: "auto", // Enable scrolling if content overflows
    }}>
      {sequence.length === 0 ? (
        <p style={{ color: "#666", fontStyle: "italic" }}>No sequence yet. Answer the agent’s questions or say "add another step" to build one.</p>
      ) : (
        sequence.map((step, i) => (
          <div key={i} style={{ marginBottom: "1.5rem" }}>
            <strong style={{ color: "#d11a2a" }}>Step {step.step}:</strong>
            <textarea
              ref={(el) => (textareaRefs.current[i] = el)}
              rows={1}
              value={step.message}
              onChange={(e) => {
                handleEdit(i, e.target.value);
                adjustTextareaHeight(textareaRefs.current[i]); // Adjust height on change
              }}
              style={{
                width: "100%",
                marginTop: "0.5rem",
                padding: "0.5rem",
                border: "1px solid #ddd",
                borderRadius: "4px",
                fontFamily: "inherit",
                fontSize: "14px",
                resize: "none", // Disable manual resizing
                overflow: "hidden", // Hide scrollbar
              }}
            />
          </div>
        ))
      )}
      {sequence.length > 0 && (
        <button
          onClick={saveEdits}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: "#d11a2a",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px",
            marginTop: "1rem",
          }}
        >
          Save Edits
        </button>
      )}
    </div>
  );
};

export default Workspace;