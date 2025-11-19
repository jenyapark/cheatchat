"use client";

import { useRouter } from "next/router";
import { useEffect, useState, useRef } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Conversation() {
  const router = useRouter();
  const { convId, tone } = router.query;

  console.log("convId:", convId); 



  const [messages, setMessages] = useState([]);
  const [cands, setCands] = useState([]);
  const [text, setText] = useState("");
  const [alias, setAlias] = useState("");

  const [relationship, setRelationship] = useState("");

  const [toneOptions, setToneOptions] = useState([]);
  const [selectedTone, setSelectedTone] = useState(null);

  const bottomRef = useRef(null);
  const prevToneRef = useRef(null);

  const scrollToBottom = () => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const saveRelationship = async () => {
  await fetch(`${API}/ui/set_relationship`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      conv_id: convId,
      relationship,
    }),

  });
  
  showToast("관계가 저장되었습니다!");
};

const handleRelationshipChange = (newRel) => {
  setRelationship(newRel);

  // 관계 바뀌면 즉시 tone options도 미리 변경
  const map = {
    close_friend: ["반말-편한","반말-장난","귀엽고 친근한 말투","담백한 반말"],
    coworker: ["친근한 존댓말","업무용 존댓말",  "유머·밈 톤", "매우 격식 있는 톤"],
    boss: ["최대한 정중한 말투","보고/업무 보고 톤"],
    acquaintance: ["부드러운 존댓말","반존칭"],
    lover: ["다정한 말투","귀엽고 애정 있는 말투","편안한 반말"],
    customer: ["공식적인 응대 톤","친절한 존댓말"]
  };

  setToneOptions(map[newRel] || []);
};

const fetchConversations = async () => {
  const res = await fetch(`${API}/ui/messages`);
  const data = await res.json();
};



  // 메시지 변경 → 자동 스크롤
useEffect(() => {
  scrollToBottom();
}, [messages]);


// 1) tone_options 가져오기
useEffect(() => {
  if (!convId) return;

  fetch(`${API}/ui/tone_options/${convId}`)
    .then((res) => res.json())
    .then((data) => {
      setRelationship(data.relationship || "");
      setToneOptions(data.tone_options || []);
    });
}, [convId]);


// 2) toneOptions 로딩 후 → selectedTone 자동 설정 (LLM 호출 X)
useEffect(() => {
  if (toneOptions.length > 0 && !selectedTone) {
    const first = toneOptions[0];
    setSelectedTone(first);  // 기본 말투 자동 선택
  }
}, [toneOptions]);


// 3) 메시지 불러오기 (대화 내용)
useEffect(() => {
  if (!convId) return;

  fetch(`${API}/ui/messages/${convId}`)
    .then(res => res.json())
    .then(data => setMessages(data.messages || []));
}, [convId]);


// 4) selectedTone 변경 → 후보 생성 
useEffect(() => {
  if (!convId || !selectedTone) return;
  if (prevToneRef.current === selectedTone) return;
  prevToneRef.current = selectedTone;

  fetch(`${API}/ui/generate_candidates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conv_id: convId, tone: selectedTone })
  })
    .then(res => res.json())
    .then(data => setCands(data.candidates || []));
}, [selectedTone, convId]);

// 5) alias 로드
useEffect(() => {
  fetch(`${API}/ui/messages`)
    .then(res => res.json())
    .then(data => {
      const found = data.conversations?.find((c) => c.id === convId);
      if (found && found.name && found.name !== convId) {
        setAlias(found.name);
      }
    });
}, [convId]);


  const showToast = (message) => {
    if (typeof document === "undefined") return;

    const toast = document.createElement("div");
    toast.innerText = message;
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

    setTimeout(() => {
      toast.style.opacity = "1";
    }, 10);

    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  };

  // alias 저장
  const saveAlias = async () => {
    await fetch(`${API}/ui/set_alias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: convId,
        alias,
      }),
    });

    showToast("이름이 저장되었습니다.");
  };

  //최종 메시지 전송
  const send = async () => {
  // 1) 메시지 전송
  await fetch(`${API}/ui/send?tone=${selectedTone}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      conversation_id: convId,
      text,
    }),
  });

  // 2) 읽음 처리
  await fetch(`${API}/ui/mark_read/${convId}`, {
    method: "POST",
  });


  // 4) 로컬 메시지 반영
  setMessages(prev => [
    ...prev,
    {
      text,
      direction: "outgoing",
      ts: Date.now() / 1000,
    }
  ]);

  fetchConversations(); 

  showToast("메시지가 전송되었습니다!");
  setText("");
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
      {/* 상단 헤더 */}
      <header
        style={{
          background: "white",
          padding: "14px 18px",
          borderRadius: 10,
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
          marginBottom: 20,
        }}
      >
        <h1 style={{ margin: 0, fontSize: 20 }}>{alias || convId}</h1>

        <section style={{ marginBottom: 20 }}>
  <h2 style={{ fontSize: 18 }}>관계 설정</h2>

  <div>현재 관계: {relationship}</div>

  <div style={{ marginTop: 10, display: "flex", gap: 8 }}>
    <select
      value={relationship}
      onChange={(e) => handleRelationshipChange(e.target.value)}
      style={{ padding: 8, borderRadius: 8 }}
    >
      <option value="close_friend">친한 친구</option>
      <option value="coworker">직장 동료</option>
      <option value="boss">상사</option>
      <option value="acquaintance">지인</option>
      <option value="lover">연인</option>
      <option value="customer">고객</option>
    </select>

    <button
      onClick={saveRelationship}
      style={{
        padding: "8px 12px",
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


        {/* 관계 기반 tone_options 버튼 UI */}
        <div style={{ marginTop: 8, display: "flex", gap: 10 }}>
          {toneOptions.map((tone) => (
            <button
              key={tone}
              onClick={() => setSelectedTone(tone)}
              style={{
                padding: "6px 12px",
                borderRadius: 8,
                border:
                  selectedTone === tone ? "2px solid #4a90e2" : "1px solid #ccc",
                background:
                  selectedTone === tone ? "#e3f2fd" : "#f9f9f9",
                cursor: "pointer",
              }}
            >
              {tone}
            </button>
          ))}
        </div>
      </header>

      {/* alias 설정 */}
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

      {/* 메시지 리스트 */}
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
              <div style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>
                {m.text}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {/* AI 후보 */}
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

      {/* 최종 메시지 입력 */}
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
