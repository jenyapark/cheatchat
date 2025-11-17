"use client";

import { useRouter } from "next/router";
import { useEffect, useState, useRef } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Conversation() {
  const router = useRouter();
  const { convId, tone = "friendly_formal" } = router.query;

  const [messages, setMessages] = useState([]);
  const [cands, setCands] = useState([]);
  const [text, setText] = useState("");
  const [alias, setAlias] = useState("");

  const bottomRef = useRef(null);

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!convId) return;

    fetch(`${API}/ui/mark_read`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: convId }),
    });

    fetch(`${API}/ui/messages/${convId}?tone=${tone}`)
      .then((res) => res.json())
      .then((data) => {
        setMessages(data.messages || []);
        setCands(data.candidates || []);
      });

    fetch(`${API}/ui/messages`)
      .then((res) => res.json())
      .then((data) => {
        const found = data.conversations.find((c) => c.id === convId);
        if (found && found.name && found.name !== convId) setAlias(found.name);
      });
  }, [convId, tone]);

  const saveAlias = async () => {
    await fetch(`${API}/ui/set_alias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: convId, alias }),
    });
    // Custom toast for alias saved
const toast2 = document.createElement("div");
toast2.innerText = "이름이 저장되었습니다";
toast2.style.position = "fixed";
toast2.style.bottom = "30px";
toast2.style.right = "30px";
toast2.style.background = "#333";
toast2.style.color = "white";
toast2.style.padding = "12px 18px";
toast2.style.borderRadius = "8px";
toast2.style.boxShadow = "0 4px 10px rgba(0,0,0,0.2)";
toast2.style.fontSize = "14px";
toast2.style.zIndex = "9999";
toast2.style.opacity = "0";
toast2.style.transition = "opacity 0.3s ease";
document.body.appendChild(toast2);
setTimeout(() => (toast2.style.opacity = "1"), 10);
setTimeout(() => {
  toast2.style.opacity = "0";
  setTimeout(() => toast2.remove(), 300);
}, 2000);
  };

  const send = async () => {
    await fetch(`${API}/ui/send?tone=${tone}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: convId, text }),
    });
    // Custom toast notification
const toast = document.createElement("div");
toast.innerText = "메시지가 전송되었습니다!";
toast.style.position = "fixed";
toast.style.bottom = "30px";
toast.style.right = "30px";
toast.style.background = "#333";
toast.style.color = "white";
toast.style.padding = "12px 18px";
toast.style.borderRadius = "8px";
toast.style.boxShadow = "0 4px 10px rgba(0,0,0,0.2)";
toast.style.fontSize = "14px";
toast.style.zIndex = "9999";
toast.style.opacity = "0";
toast.style.transition = "opacity 0.3s ease";
document.body.appendChild(toast);
setTimeout(() => (toast.style.opacity = "1"), 10);
setTimeout(() => {
  toast.style.opacity = "0";
  setTimeout(() => toast.remove(), 300);
}, 2000);
  };

  return (
    <div
      style={{
        padding: 20,
        maxWidth: 800,
        margin: "0 auto",
        fontFamily: "-apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <header
        style={{
          background: "white",
          padding: "14px 18px",
          borderRadius: 10,
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
          marginBottom: 20,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: 20 }}>{alias || convId}</h1>
          <div style={{ color: "#666", fontSize: 14 }}>
            말투: {
              tone === "friendly_formal"
                ? "친근한 존댓말"
                : tone === "soft_formal"
                ? "부드러운 포멀"
                : "편한 반말"
            }
          </div>
        </div>
      </header>

      <section style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 18 }}>대화 상대 이름 설정</h2>
        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <input
            value={alias}
            onChange={(e) => setAlias(e.target.value)}
            style={{
              flex: 1,
              padding: 10,
              borderRadius: 8,
              border: "1px solid #ccc",
            }}
          />
          <button
            onClick={saveAlias}
            style={{
              padding: "10px 16px",
              borderRadius: 8,
              background: "#4a90e2",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
          >
            저장
          </button>
        </div>
      </section>

      <div
        style={{
          background: "#fafafa",
          borderRadius: 10,
          padding: 16,
          height: 400,
          overflowY: "auto",
          boxShadow: "inset 0 0 8px rgba(0,0,0,0.05)",
          marginBottom: 20,
          display: "flex",
          flexDirection: "column",
          gap: 10,
        }}
      >
        {messages.map((m, idx) => {
          const isMe = m.direction === "outgoing";
          return (
            <div
              key={idx}
              style={{
                alignSelf: isMe ? "flex-end" : "flex-start",
                background: isMe ? "#d0ebff" : "white",
                padding: "10px 14px",
                borderRadius: 10,
                maxWidth: "70%",
                boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
              }}
            >
              <b>{isMe ? "나" : "상대"}</b>
              <div style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>{m.text}</div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <section style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 18 }}>AI 추천 답장</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {cands.map((c, idx) => (
            <div
              key={idx}
              onClick={() => setText(c)}
              style={{
                background: "white",
                padding: 12,
                borderRadius: 10,
                cursor: "pointer",
                boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
                border: "1px solid #e5e5e5",
              }}
            >
              {c}
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 style={{ fontSize: 18 }}>최종 메시지</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          style={{
            width: "100%",
            padding: 12,
            borderRadius: 10,
            border: "1px solid #ccc",
            marginTop: 8,
          }}
        />

        <button
          onClick={send}
          style={{
            marginTop: 12,
            padding: "12px 16px",
            borderRadius: 10,
            background: "#4caf50",
            color: "white",
            border: "none",
            cursor: "pointer",
            fontSize: 16,
          }}
        >
          보내기
        </button>
      </section>
    </div>
  );
}
