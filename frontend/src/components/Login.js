import React, { useState } from 'react';

function Login({ onLogin }) {
  // Toggle to decide which form to show: login or sign-up
  const [isSignUpMode, setIsSignUpMode] = useState(false);

  // Shared fields
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Only used in sign-up mode
  const [email, setEmail] = useState("");

  // Handle the LOGIN flow
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.error || "Login failed");
        return;
      }
      // success => data = { success: true, user_id, username }
      onLogin({ user_id: data.user_id, username: data.username });
    } catch (err) {
      console.error("Login error:", err);
      alert("Error connecting to server.");
    }
  };

  // Handle the SIGN-UP flow
  const handleSignUpSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data.error || "Sign-up failed");
        return;
      }
      // success => data = { success: true, user_id, username, email }
      alert(`Sign-up success for ${data.username}! You can now log in.`);
      // Optionally auto-login here, or just switch to login mode
      setIsSignUpMode(false);
    } catch (err) {
      console.error("SignUp error:", err);
      alert("Error connecting to server.");
    }
  };

  return (
    <div 
      style={{ 
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh"
      }}
    >
      {/* Switch heading based on mode */}
      <h1>{isSignUpMode ? "Sign Up" : "Login"}</h1>

      {/* Conditionally render the appropriate form */}
      {isSignUpMode ? (
        // SIGN-UP form
        <form
          onSubmit={handleSignUpSubmit}
          style={{ width: "300px", display: "flex", flexDirection: "column" }}
        >
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e)=>setUsername(e.target.value)}
            style={{ marginBottom: "1rem", padding: "0.5rem" }}
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
            style={{ marginBottom: "1rem", padding: "0.5rem" }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            style={{ marginBottom: "1rem", padding: "0.5rem" }}
          />
          <button
            type="submit"
            style={{
              padding: "0.5rem",
              backgroundColor: "#d11a2a",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            Sign Up
          </button>
        </form>
      ) : (
        // LOGIN form
        <form
          onSubmit={handleLoginSubmit}
          style={{ width: "300px", display: "flex", flexDirection: "column" }}
        >
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e)=>setUsername(e.target.value)}
            style={{ marginBottom: "1rem", padding: "0.5rem" }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
            style={{ marginBottom: "1rem", padding: "0.5rem" }}
          />
          <button
            type="submit"
            style={{
              padding: "0.5rem",
              backgroundColor: "#d11a2a",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            Login
          </button>
        </form>
      )}

      {/* Toggle Link */}
      <p style={{ marginTop: "1rem" }}>
        {isSignUpMode ? (
          <>
            Already have an account?{" "}
            <span 
              onClick={() => setIsSignUpMode(false)} 
              style={{ color: "#007bff", cursor: "pointer" }}
            >
              Log in
            </span>
          </>
        ) : (
          <>
            Don&apos;t have an account?{" "}
            <span 
              onClick={() => setIsSignUpMode(true)} 
              style={{ color: "#007bff", cursor: "pointer" }}
            >
              Sign up
            </span>
          </>
        )}
      </p>
    </div>
  );
}

export default Login;
