"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [list, setList] = useState([]);

  useEffect(() => {
    const url = `${API}/ui/messages`;
    fetch(url)
      .then(async (r) => {
        const text = await r.text();
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
    <div style={{ padding: 20, maxWidth: 720, margin: "0 auto", fontFamily: "-apple-system, BlinkMacSystemFont, sans-serif" }}>
      <h1 style={{ fontSize: 26, marginBottom: 20 }}>DM 목록</h1>

      {list.length === 0 && (
        <div style={{ padding: 40, textAlign: "center", color: "#777" }}>
          아직 들어온 DM이 없습니다.
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {list.map(item => (
          <Link
            key={item.id}
            href={`/${item.id}`}
            style={{
              textDecoration: "none",
              color: "inherit",
              background: "white",
              padding: "16px 20px",
              borderRadius: 12,
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
              display: "block",
              transition: "0.2s all",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: "bold", fontSize: 17 }}>
                {item.name}
              </div>

              {item.unreadCount > 0 && (
                <div style={{
                  backgroundColor: "#ff5252",
                  color: "white",
                  padding: "3px 10px",
                  borderRadius: "14px",
                  fontSize: 12,
                  fontWeight: "bold",
                }}>
                  {item.unreadCount}
                </div>
              )}
            </div>

            <div style={{ marginTop: 8, fontSize: 14, color: "#444" }}>
              {item.preview}
            </div>

            <div style={{ marginTop: 6, fontSize: 12, color: "#888" }}>
              {item.time}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}