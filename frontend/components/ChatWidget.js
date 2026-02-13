"use client";

import { useState, useEffect, useRef } from "react";

export default function ChatWidget() {
  const BACKEND = process.env.NEXT_PUBLIC_API_URL;

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("English");

  const messagesEndRef = useRef(null);

  // Safety check
  useEffect(() => {
    if (!BACKEND) {
      console.error("NEXT_PUBLIC_API_URL is NOT defined!");
    }
  }, [BACKEND]);

  // Auto detect browser language
  useEffect(() => {
    const browserLang = navigator.language.toLowerCase();

    if (browserLang.includes("hi")) setLanguage("Hindi");
    else if (browserLang.includes("mr")) setLanguage("Marathi");
    else if (browserLang.includes("gu")) setLanguage("Gujarati");
    else if (browserLang.includes("ta")) setLanguage("Tamil");
    else if (browserLang.includes("te")) setLanguage("Telugu");
    else setLanguage("English");
  }, []);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text) => {
    if (!BACKEND) {
      alert("Backend URL not configured.");
      return;
    }

    const query = text || input;
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, language })
      });

      if (!res.ok) {
        throw new Error("Server error");
      }

      // 🔥 IMPORTANT: Backend returns TEXT, not JSON
      const responseText = await res.text();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: responseText || "No response available."
        }
      ]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "⚠️ System busy or API limit reached. Please try again later."
        }
      ]);
    }

    setLoading(false);
  };

  return (
    <>
      {/* Floating Button */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          position: "fixed",
          bottom: "25px",
          right: "25px",
          width: "60px",
          height: "60px",
          borderRadius: "50%",
          backgroundColor: "#c62828",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          boxShadow: "0 5px 20px rgba(0,0,0,0.3)",
          zIndex: 999
        }}
      >
        <span style={{ color: "white", fontSize: "26px" }}>💬</span>
      </div>

      {open && (
        <div
          style={{
            position: "fixed",
            bottom: "100px",
            right: "25px",
            width: "380px",
            maxWidth: "95%",
            height: "580px",
            backgroundColor: "white",
            borderRadius: "15px",
            boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            zIndex: 999
          }}
        >
          {/* Header */}
          <div
            style={{
              background: "linear-gradient(90deg, #c62828, #8e0000)",
              padding: "12px",
              color: "white",
              display: "flex",
              justifyContent: "space-between"
            }}
          >
            APSIT Assistant

            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              style={{ borderRadius: "6px", fontSize: "12px" }}
            >
              <option>English</option>
              <option>Hindi</option>
              <option>Marathi</option>
              <option>Gujarati</option>
              <option>Tamil</option>
              <option>Telugu</option>
            </select>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              padding: "12px",
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: "8px"
            }}
          >
            {messages.map((msg, index) => (
              <div
                key={index}
                style={{
                  alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                  backgroundColor:
                    msg.role === "user" ? "#c62828" : "#f1f1f1",
                  color: msg.role === "user" ? "white" : "#333",
                  padding: "8px 12px",
                  borderRadius: "15px",
                  maxWidth: "75%"
                }}
              >
                {msg.content}
              </div>
            ))}

            {loading && <div style={{ fontSize: "12px" }}>Typing...</div>}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div
            style={{
              padding: "10px",
              borderTop: "1px solid #eee",
              display: "flex",
              gap: "6px"
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Type your message..."
              style={{
                flex: 1,
                padding: "6px 8px",
                borderRadius: "6px",
                border: "1px solid #ddd"
              }}
            />

            <button
              onClick={() => sendMessage()}
              style={{
                backgroundColor: "#c62828",
                border: "none",
                color: "white",
                padding: "6px 10px",
                borderRadius: "6px",
                cursor: "pointer"
              }}
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}
