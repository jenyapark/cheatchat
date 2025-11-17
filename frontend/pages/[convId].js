"use client";

import { useRouter } from "next/router";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Conversation() {
  const router = useRouter();
  const { convId, tone = "friendly_formal" } = router.query;  

  const [messages, setMessages] = useState([]);
  const [cands, setCands] = useState([]);
  const [text, setText] = useState("");

  const [alias, setAlias] = useState("");

  // 대화 내용 로드
  useEffect(() => {
    if (!convId) return;

    // 읽음 처리
    fetch(`${API}/ui/mark_read`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: convId })
    });

    // 메시지 / 후보 불러오기 (tone 포함)
    fetch(`${API}/ui/messages/${convId}?tone=${tone}`)
      .then((res) => res.json())
      .then((data) => {
        setMessages(data.messages || []);
        setCands(data.candidates || []);
      })
      .catch(console.error);

    // alias 불러오기
    fetch(`${API}/ui/messages`)
      .then((res) => res.json())
      .then((data) => {
        const found = data.conversations.find((c) => c.id === convId);
        if (found && found.name && found.name !== convId) {
          setAlias(found.name);
        }
      });
  }, [convId, tone]);   

  // alias 저장 함수
  const saveAlias = async () => {
    await fetch(`${API}/ui/set_alias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: convId,
        alias,
      }),
    });

    alert("이름 저장됨!");
  };

  // 메시지 보내기 (tone 적용)
  const send = async () => {
    await fetch(`${API}/ui/send?tone=${tone}`, {    
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: convId,
        text,
      }),
    });

    alert("보냈습니다!");
  };

  return (
    <div style={{ padding: 20 }}>
      
      {/* 말투 보기용 UI */}
      <div style={{
        background: "#f7f7f7",
        padding: "10px 12px",
        borderRadius: 8,
        marginBottom: 20
      }}>
        <b>현재 말투:</b>{" "}
        {tone === "friendly_formal" && "친근한 존댓말"}
        {tone === "soft_formal" && "부드러운 포멀"}
        {tone === "casual" && "편한 반말"}
      </div>

      {/* alias UI */}
      <h2>대화 상대 이름 설정</h2>
      <input
        value={alias}
        onChange={(e) => setAlias(e.target.value)}
        placeholder="예: 지윤, 민재, 현민언니"
        style={{ padding: 8, width: "70%", marginRight: 8 }}
      />
      <button onClick={saveAlias} style={{ padding: "8px 12px" }}>
        저장
      </button>

      <h1 style={{ marginTop: 20 }}>대화방: {alias || convId}</h1>

      <h2>메시지</h2>
      {messages.map((m, idx) => (
        <div key={idx}>
          [{m.direction}] {m.text}
        </div>
      ))}

      <h2>AI 후보</h2>
      {cands.map((c, idx) => (
        <button
          key={idx}
          onClick={() => setText(c)}
          style={{
            display: "block",
            marginBottom: 6,
            padding: "6px 10px",
          }}
        >
          {c}
        </button>
      ))}

      <h2>최종 메시지</h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={5}
        style={{ width: "100%" }}
      />

      <br />
      <button
        onClick={send}
        style={{ marginTop: 10, padding: "10px 15px" }}
      >
        보내기
      </button>
    </div>
  );
}

