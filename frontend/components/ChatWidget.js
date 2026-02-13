"use client";

import { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("Auto");
  const [translatedIntents, setTranslatedIntents] = useState([]);

  const messagesEndRef = useRef(null);

  const masterIntents = [
    "Admissions",
    "Courses Offered",
    "Placements",
    "Contact Details"
  ];

  const supportedLanguages = [
    "English","Hindi","Marathi","Gujarati","Tamil","Telugu",
    "Kannada","Malayalam","Bengali","Punjabi","Odia","Assamese",
    "Urdu","Sanskrit","Konkani","Manipuri","Bodo","Dogri",
    "Maithili","Santali","Nepali","Kashmiri"
  ];

  // 🧠 Auto detect browser language
  useEffect(() => {
    const browserLang = navigator.language;

    const match = supportedLanguages.find((lang) =>
      browserLang.toLowerCase().includes(lang.slice(0, 2).toLowerCase())
    );

    if (match) {
      setLanguage(match);
    }
  }, []);

  // 🔄 Scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 🌍 Translate intents when language changes
  useEffect(() => {
    const translateIntents = async () => {
      if (language === "English" || language === "Auto") {
        setTranslatedIntents(masterIntents);
        return;
      }

      try {
        const res = await axios.post(
          "https://apsit-ai-assistant-production.up.railway.app/translate/",
          {
            texts: masterIntents,
            language
          }
        );

        setTranslatedIntents(res.data.translations);
      } catch {
        setTranslatedIntents(masterIntents);
      }
    };

    translateIntents();
  }, [language]);

  const sendMessage = async (text) => {
    const query = text || input;
    if (!query.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(
        "https://apsit-ai-assistant-production.up.railway.app/chat/",
        {
          query,
          language
        }
      );

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.answer || res.data }
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong." }
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
              style={{
                borderRadius: "6px",
                fontSize: "12px"
              }}
            >
              <option value="Auto">Auto</option>
              {supportedLanguages.map((lang, i) => (
                <option key={i}>{lang}</option>
              ))}
            </select>
          </div>

          {/* Suggested Intents */}
          <div
            style={{
              padding: "8px",
              display: "flex",
              flexWrap: "wrap",
              gap: "6px",
              backgroundColor: "#f9f9f9"
            }}
          >
            {translatedIntents.map((item, index) => (
              <button
                key={index}
                onClick={() => sendMessage(item)}
                style={{
                  padding: "5px 10px",
                  borderRadius: "15px",
                  border: "1px solid #c62828",
                  backgroundColor: "white",
                  color: "#c62828",
                  cursor: "pointer",
                  fontSize: "11px"
                }}
              >
                {item}
              </button>
            ))}
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
