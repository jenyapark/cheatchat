"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [tone, setTone] = useState("friendly_formal");
  const [list, setList] = useState([]);

  useEffect(() => {
    const url = `${API}/ui/messages`;
    console.log("FETCHING:", url);

    fetch(url, {
      headers: {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
      }
    })
      .then(async (r) => {
        const text = await r.text();
        console.log("STATUS =", r.status);
        console.log("BODY =", text.substring(0, 300));

        try {
          const data = JSON.parse(text);
          setList(data.conversations || []);
        } catch (e) {
          console.log("JSON parse error", e);
        }
      })
      .catch(err => console.error("FETCH ERROR =", err));
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>DM 목록</h1>

      {/* 말투 선택*/}
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontWeight: "bold", marginBottom: 8 }}>말투 선택</div>

        <div style={{ display: "flex", gap: "12px", fontSize: "14px" }}>
          
          <label style={{ cursor: "pointer" }}>
            <input
              type="radio"
              name="tone"
              value="friendly_formal"
              checked={tone === "friendly_formal"}
              onChange={() => setTone("friendly_formal")}
              style={{ marginRight: 6 }}
            />
            친근한 존댓말
          </label>

          <label style={{ cursor: "pointer" }}>
            <input
              type="radio"
              name="tone"
              value="soft_formal"
              checked={tone === "soft_formal"}
              onChange={() => setTone("soft_formal")}
              style={{ marginRight: 6 }}
            />
            부드러운 포멀
          </label>

          <label style={{ cursor: "pointer" }}>
            <input
              type="radio"
              name="tone"
              value="casual"
              checked={tone === "casual"}
              onChange={() => setTone("casual")}
              style={{ marginRight: 6 }}
            />
            편한 반말
          </label>

        </div>
      </div>
      {/*  [추가 영역 끝]  */}

      {list.length === 0 && <div>아직 들어온 DM 없음</div>}

      {list.map(item => (
        <div 
          key={item.id} 
          style={{
            marginBottom: 16,
            padding: "12px 0",
            borderBottom: "1px solid #ddd",
          }}
        >
          <Link 
            href={`/${item.id}?tone=${tone}`} 
            style={{ textDecoration: "none", color: "inherit" }}>

            {/* 상단: 이름 + 숫자 배지 */}
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <div style={{ 
                fontWeight: "bold", 
                fontSize: "16px" 
              }}>
                {item.name}
              </div>

              {/* unreadCount > 0이면 숫자 배지 표시 */}
              {item.unreadCount > 0 && (
                <div style={{
                  backgroundColor: "red",
                  color: "white",
                  padding: "2px 8px",
                  borderRadius: "12px",
                  fontSize: "12px",
                  fontWeight: "bold"
                }}>
                  {item.unreadCount}
                </div>
              )}
            </div>

            {/* 마지막 메시지 미리보기 */}
            <div style={{ marginTop: 6, fontSize: "14px" }}>
              {item.preview}
            </div>

            {/* 시간 */}
            <div style={{ 
              fontSize: "12px", 
              color: "#666",
              marginTop: 4 
            }}>
              {item.time}
            </div>

          </Link>
        </div>
      ))}
    </div>
  );
}
