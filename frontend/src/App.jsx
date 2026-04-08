import { useState, useRef, useEffect, useCallback } from "react"
import axios from "axios"
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from "recharts"

const BACKEND = "http://127.0.0.1:8000"

const SUGGESTIONS = [
  "Which state has the highest ground water availability?",
  "Show rainfall data for Punjab in 2022-23",
  "Top 5 districts by ground water recharge",
  "What is the stage of ground water extraction in Rajasthan?",
]

// ─── Unique chat ID ────────────────────────────────────────────────────────────
let _id = 0
const uid = () => `chat_${++_id}_${Date.now()}`

// ─── Parse answer into structured content ─────────────────────────────────────
function parseAnswer(text) {
  const numberedList = text.match(/\d+\.\s+.+/g)
  if (numberedList && numberedList.length >= 2) {
    const intro = text.split(/1\.\s/)[0].trim()
    const items = numberedList.map(line => {
      const match = line.match(/\d+\.\s+(.+?):\s*(.+)/)
      if (match) return { label: match[1].trim(), value: match[2].trim() }
      return { label: line.replace(/^\d+\.\s*/, '').trim(), value: null }
    })
    return { type: "list", intro, items }
  }
  return { type: "text", content: text }
}

// ─── Extract chart data from a ranked list ────────────────────────────────────
function extractChartData(items) {
  return items
    .map(item => {
      if (!item.value) return null
      const numMatch = item.value.match(/[\d,]+\.?\d*/)
      if (!numMatch) return null
      const num = parseFloat(numMatch[0].replace(/,/g, ''))
      if (isNaN(num)) return null
      return { name: item.label.length > 14 ? item.label.slice(0, 14) + "…" : item.label, value: num, full: item.label }
    })
    .filter(Boolean)
}

const CHART_COLORS = ["#38bdf8", "#34d399", "#fb923c", "#a78bfa", "#f472b6", "#facc15", "#60a5fa", "#4ade80"]

// ─── Custom chart tooltip ──────────────────────────────────────────────────────
function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: "rgba(8,24,48,0.97)",
      border: "1px solid rgba(125,211,252,0.2)",
      borderRadius: 10,
      padding: "8px 14px",
      fontSize: 12,
      color: "#e0f2fe",
    }}>
      <div style={{ fontWeight: 600, marginBottom: 2 }}>{payload[0].payload.full || payload[0].payload.name}</div>
      <div style={{ color: "#7dd3fc" }}>{payload[0].value?.toLocaleString()} ham</div>
    </div>
  )
}

// ─── Chart component ──────────────────────────────────────────────────────────
function DataChart({ items }) {
  const data = extractChartData(items)
  if (!data || data.length < 2) return null
  const isTimeSeries = items.some(i => /\d{4}/.test(i.label))

  return (
    <div style={{
      marginTop: 16,
      padding: "14px 6px 6px",
      background: "rgba(8,24,48,0.6)",
      borderRadius: 12,
      border: "1px solid rgba(125,211,252,0.1)",
    }}>
      <div style={{ fontSize: 11, color: "#475569", marginBottom: 10, paddingLeft: 8, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em" }}>
        {isTimeSeries ? "Trend" : "Comparison"} Chart
      </div>
      <ResponsiveContainer width="100%" height={180}>
        {isTimeSeries ? (
          <LineChart data={data} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(125,211,252,0.07)" />
            <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} width={40} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={2} dot={{ fill: "#38bdf8", r: 3 }} activeDot={{ r: 5 }} />
          </LineChart>
        ) : (
          <BarChart data={data} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(125,211,252,0.07)" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} width={40} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="value" radius={[5, 5, 0, 0]}>
              {data.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} fillOpacity={0.85} />)}
            </Bar>
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}

// ─── Ranked list component ────────────────────────────────────────────────────
function RankedList({ intro, items }) {
  const chartData = extractChartData(items)
  const showChart = chartData && chartData.length >= 2

  return (
    <div>
      {intro && <p style={{ fontSize: 13, color: "#94a3b8", marginBottom: 12, fontWeight: 300 }}>{intro}</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
        {items.map((item, i) => {
          const medals = ["#f59e0b", "#94a3b8", "#cd7c2f"]
          const badgeColor = i < 3 ? medals[i] : "#0ea5e9"
          return (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: 10,
              padding: "8px 12px",
              background: "rgba(14,165,233,0.06)",
              border: "1px solid rgba(125,211,252,0.09)",
              borderRadius: 10,
              transition: "background 0.2s",
            }}>
              <div style={{
                width: 24, height: 24, borderRadius: "50%",
                background: badgeColor,
                color: "#fff", fontSize: 11, fontWeight: 700,
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0,
                boxShadow: i < 3 ? `0 0 8px ${badgeColor}66` : "none",
              }}>{i + 1}</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 1, minWidth: 0 }}>
                <span style={{ fontSize: 13, fontWeight: 500, color: "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.label}</span>
                {item.value && <span style={{ fontSize: 12, color: "#7dd3fc" }}>{item.value}</span>}
              </div>
            </div>
          )
        })}
      </div>
      {showChart && <DataChart items={items} />}
    </div>
  )
}

// ─── Typing effect hook ───────────────────────────────────────────────────────
function useTypingEffect(fullText, enabled, speed = 8) {
  const [displayed, setDisplayed] = useState("")
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (!enabled || !fullText) {
      setDisplayed(fullText || "")
      setDone(true)
      return
    }
    setDisplayed("")
    setDone(false)
    let i = 0
    // Chunk typing: add multiple chars per tick for speed
    const chunkSize = Math.max(1, Math.floor(fullText.length / 120))
    const timer = setInterval(() => {
      i += chunkSize
      if (i >= fullText.length) {
        setDisplayed(fullText)
        setDone(true)
        clearInterval(timer)
      } else {
        setDisplayed(fullText.slice(0, i))
      }
    }, speed)
    return () => clearInterval(timer)
  }, [fullText, enabled, speed])

  return { displayed, done }
}

// ─── Bot message with typing effect ──────────────────────────────────────────
function BotMessage({ text, animate }) {
  const { displayed, done } = useTypingEffect(text, animate)
  const parsed = parseAnswer(displayed)

  return (
    <div style={{ position: "relative" }}>
      {parsed.type === "list"
        ? <RankedList intro={parsed.intro} items={parsed.items} />
        : <span style={{ whiteSpace: "pre-wrap", lineHeight: 1.7 }}>{displayed}</span>
      }
      {!done && (
        <span style={{
          display: "inline-block", width: 2, height: "1em",
          background: "#38bdf8", marginLeft: 2,
          animation: "cursorBlink 0.7s step-end infinite",
          verticalAlign: "text-bottom",
        }} />
      )}
    </div>
  )
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────
function Sidebar({ chats, activeChatId, onSelect, onNew, collapsed, onToggle }) {
  return (
    <>
      {/* Overlay for mobile */}
      {!collapsed && (
        <div onClick={onToggle} style={{
          display: "none",
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 40,
          "@media (max-width: 768px)": { display: "block" }
        }} className="sidebar-overlay" />
      )}
      <aside style={{
        width: collapsed ? 0 : 240,
        minWidth: collapsed ? 0 : 240,
        height: "100vh",
        background: "rgba(4,14,28,0.97)",
        borderRight: "1px solid rgba(125,211,252,0.08)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        transition: "width 0.25s ease, min-width 0.25s ease",
        flexShrink: 0,
        zIndex: 50,
      }}>
        {/* Sidebar header */}
        <div style={{
          padding: "18px 14px 12px",
          borderBottom: "1px solid rgba(125,211,252,0.07)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexShrink: 0,
        }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: "#475569", textTransform: "uppercase", letterSpacing: "0.08em", whiteSpace: "nowrap" }}>
            Chat History
          </span>
          <button onClick={onNew} title="New Chat" style={{
            background: "rgba(14,165,233,0.12)",
            border: "1px solid rgba(14,165,233,0.2)",
            borderRadius: 8, color: "#38bdf8",
            width: 30, height: 30,
            cursor: "pointer", fontSize: 18, lineHeight: 1,
            display: "flex", alignItems: "center", justifyContent: "center",
            transition: "background 0.2s",
            flexShrink: 0,
          }}>+</button>
        </div>

        {/* Chat list */}
        <div style={{ flex: 1, overflowY: "auto", padding: "8px 8px", display: "flex", flexDirection: "column", gap: 3, scrollbarWidth: "thin", scrollbarColor: "rgba(125,211,252,0.1) transparent" }}>
          {chats.length === 0 && (
            <div style={{ color: "#334155", fontSize: 12, padding: "12px 8px", textAlign: "center" }}>No chats yet</div>
          )}
          {chats.map(chat => (
            <button key={chat.id} onClick={() => onSelect(chat.id)} style={{
              width: "100%", textAlign: "left",
              background: chat.id === activeChatId ? "rgba(14,165,233,0.12)" : "transparent",
              border: chat.id === activeChatId ? "1px solid rgba(14,165,233,0.2)" : "1px solid transparent",
              borderRadius: 8, padding: "8px 10px",
              cursor: "pointer",
              transition: "background 0.15s, border-color 0.15s",
              whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
              fontSize: 13, color: chat.id === activeChatId ? "#bae6fd" : "#64748b",
              fontFamily: "'DM Sans', sans-serif",
            }}>
              💬 {chat.title}
            </button>
          ))}
        </div>

        {/* Sidebar footer */}
        <div style={{
          padding: "12px 14px",
          borderTop: "1px solid rgba(125,211,252,0.07)",
          fontSize: 10,
          color: "#1e3a5f",
          flexShrink: 0,
          whiteSpace: "nowrap",
        }}>
          INGRES · CGWB · Ministry of Jal Shakti
        </div>
      </aside>
    </>
  )
}

// ─── Water drops background ───────────────────────────────────────────────────
function WaterDrops() {
  return (
    <div style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0, overflow: "hidden" }} aria-hidden>
      {[
        { w: 340, h: 340, left: "-80px", top: "10%", dur: "18s", delay: "0s" },
        { w: 200, h: 200, right: "5%", top: "30%", dur: "14s", delay: "-4s" },
        { w: 260, h: 260, left: "30%", bottom: "-60px", dur: "20s", delay: "-8s" },
        { w: 160, h: 160, right: "20%", bottom: "20%", dur: "16s", delay: "-2s" },
        { w: 400, h: 400, right: "-120px", top: "-60px", dur: "22s", delay: "-10s", opacity: 0.03 },
      ].map((d, i) => (
        <div key={i} style={{
          position: "absolute",
          borderRadius: "50%",
          opacity: d.opacity ?? 0.05,
          background: "radial-gradient(circle at 40% 35%, #7dd3fc, #0ea5e9 60%, #0369a1)",
          width: d.w, height: d.h,
          left: d.left, right: d.right, top: d.top, bottom: d.bottom,
          animation: `floatDrop ${d.dur} linear ${d.delay} infinite`,
        }} />
      ))}
    </div>
  )
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [chats, setChats] = useState([])          // [{id, title, messages}]
  const [activeChatId, setActiveChatId] = useState(null)
  const [question, setQuestion] = useState("")
  const [loading, setLoading] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  const activeChat = chats.find(c => c.id === activeChatId)
  const messages = activeChat?.messages ?? []

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "46px"
    el.style.height = Math.min(el.scrollHeight, 120) + "px"
  }, [question])

  // Responsive: collapse sidebar on small screens by default
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 768px)")
    if (mq.matches) setSidebarCollapsed(true)
    const handler = e => setSidebarCollapsed(e.matches)
    mq.addEventListener("change", handler)
    return () => mq.removeEventListener("change", handler)
  }, [])

  const newChat = useCallback(() => {
    const id = uid()
    setChats(prev => [{ id, title: "New Chat", messages: [] }, ...prev])
    setActiveChatId(id)
    setQuestion("")
  }, [])

  // Create first chat on mount
  useEffect(() => { newChat() }, [])

  const send = async (q) => {
    const text = (q || question).trim()
    if (!text || loading) return

    // Ensure there's an active chat
    let chatId = activeChatId
    if (!chatId) { newChat(); return }

    const userMsg = { role: "user", text, id: uid() }
    setChats(prev => prev.map(c => {
      if (c.id !== chatId) return c
      const updated = [...c.messages, userMsg]
      return {
        ...c,
        messages: updated,
        title: c.title === "New Chat" ? text.slice(0, 32) + (text.length > 32 ? "…" : "") : c.title,
      }
    }))
    setQuestion("")
    setLoading(true)

    try {
      const res = await axios.post(`${BACKEND}/chat`, { question: text })
      const botMsg = { role: "bot", text: res.data.answer, id: uid(), animate: true }
      setChats(prev => prev.map(c =>
        c.id !== chatId ? c : { ...c, messages: [...c.messages, botMsg] }
      ))
    } catch {
      const errMsg = { role: "bot", text: "⚠️ Could not reach the backend. Make sure the server is running on port 8000.", id: uid(), animate: false }
      setChats(prev => prev.map(c =>
        c.id !== chatId ? c : { ...c, messages: [...c.messages, errMsg] }
      ))
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send() }
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        html, body, #root {
          height: 100%;
          width: 100%;
          overflow: hidden;
          background: #050e1a;
          font-family: 'DM Sans', sans-serif;
        }

        .app-shell {
          display: flex;
          width: 100vw;
          height: 100vh;
          overflow: hidden;
          position: relative;
        }

        .main-panel {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
          height: 100vh;
          overflow: hidden;
          position: relative;
          z-index: 5;
        }

        /* Header */
        .header {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 20px;
          background: rgba(5,14,28,0.92);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(125,211,252,0.1);
          flex-shrink: 0;
          z-index: 20;
        }

        .toggle-btn {
          background: transparent;
          border: 1px solid rgba(125,211,252,0.12);
          border-radius: 8px;
          color: #475569;
          width: 34px; height: 34px;
          cursor: pointer;
          display: flex; align-items: center; justify-content: center;
          transition: all 0.2s;
          flex-shrink: 0;
        }
        .toggle-btn:hover { color: #7dd3fc; border-color: rgba(125,211,252,0.3); background: rgba(14,165,233,0.08); }

        .header-logo {
          width: 38px; height: 38px;
          border-radius: 10px;
          background: linear-gradient(135deg, #0ea5e9, #0369a1);
          display: flex; align-items: center; justify-content: center;
          flex-shrink: 0;
          box-shadow: 0 0 18px rgba(14,165,233,0.3);
        }

        .header-name {
          font-family: 'DM Serif Display', serif;
          font-size: 17px; color: #e0f2fe;
        }

        .header-sub { font-size: 11px; color: #7dd3fc; opacity: 0.6; font-weight: 300; margin-top: 1px; }

        .header-pill {
          margin-left: auto;
          display: flex; align-items: center; gap: 6px;
          font-size: 11px; color: #34d399; font-weight: 500;
          background: rgba(52,211,153,0.08);
          border: 1px solid rgba(52,211,153,0.18);
          border-radius: 20px; padding: 4px 11px;
        }

        .pulse-dot {
          width: 6px; height: 6px; border-radius: 50%;
          background: #34d399;
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.7)} }

        /* Messages */
        .messages {
          flex: 1;
          overflow-y: auto;
          padding: 24px 0;
          display: flex;
          flex-direction: column;
          gap: 16px;
          scrollbar-width: thin;
          scrollbar-color: rgba(125,211,252,0.15) transparent;
        }

        .messages-inner {
          width: 100%;
          max-width: 760px;
          margin: 0 auto;
          padding: 0 20px;
        }

        /* Welcome */
        .welcome {
          text-align: center;
          padding: 48px 0 16px;
          animation: fadeUp 0.5s ease both;
        }

        .welcome-icon { font-size: 52px; display: block; margin-bottom: 14px; filter: drop-shadow(0 0 22px rgba(14,165,233,0.55)); }
        .welcome-title { font-family: 'DM Serif Display', serif; font-size: 28px; color: #e0f2fe; margin-bottom: 10px; }
        .welcome-sub { font-size: 14px; color: #94a3b8; max-width: 400px; margin: 0 auto 26px; line-height: 1.75; font-weight: 300; }

        .chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
        .chip {
          font-family: 'DM Sans', sans-serif;
          font-size: 12px; padding: 7px 15px;
          border: 1px solid rgba(125,211,252,0.18); border-radius: 20px;
          cursor: pointer; color: #7dd3fc;
          background: rgba(14,165,233,0.07);
          transition: all 0.2s; font-weight: 400;
        }
        .chip:hover { background: rgba(14,165,233,0.15); border-color: rgba(125,211,252,0.38); color: #bae6fd; transform: translateY(-1px); }

        /* Message rows */
        .msg-row {
          display: flex; gap: 10px; align-items: flex-start;
          animation: fadeUp 0.3s ease both;
        }
        .msg-row.user { flex-direction: row-reverse; }

        .avatar {
          width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
          display: flex; align-items: center; justify-content: center;
          font-size: 10px; font-weight: 600; letter-spacing: 0.02em;
          margin-top: 2px;
        }
        .avatar.bot { background: linear-gradient(135deg, #0ea5e9, #0369a1); color: #e0f2fe; box-shadow: 0 0 12px rgba(14,165,233,0.35); }
        .avatar.user { background: rgba(148,163,184,0.12); color: #64748b; border: 1px solid rgba(148,163,184,0.18); }

        .bubble {
          max-width: min(72%, 560px);
          padding: 12px 16px; border-radius: 18px;
          font-size: 14px; line-height: 1.7;
        }
        .bubble.bot {
          background: rgba(10,26,50,0.85);
          border: 1px solid rgba(125,211,252,0.1);
          color: #cbd5e1;
          border-top-left-radius: 4px;
          backdrop-filter: blur(8px);
        }
        .bubble.user {
          background: linear-gradient(135deg, rgba(14,165,233,0.22), rgba(3,105,161,0.28));
          border: 1px solid rgba(125,211,252,0.18);
          color: #bae6fd;
          border-top-right-radius: 4px;
        }

        /* Typing indicator */
        .typing-dots { display: flex; gap: 5px; padding: 4px 2px; }
        .typing-dot {
          width: 7px; height: 7px; border-radius: 50%;
          background: #0ea5e9;
          animation: typingBounce 1.2s ease-in-out infinite;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.16s; }
        .typing-dot:nth-child(3) { animation-delay: 0.32s; }
        @keyframes typingBounce { 0%,80%,100%{transform:translateY(0);opacity:0.3} 40%{transform:translateY(-7px);opacity:1} }

        /* Input */
        .input-area {
          flex-shrink: 0;
          padding: 14px 20px;
          background: rgba(5,14,28,0.94);
          backdrop-filter: blur(20px);
          border-top: 1px solid rgba(125,211,252,0.09);
          z-index: 20;
        }
        .input-inner {
          max-width: 760px; margin: 0 auto;
          display: flex; gap: 10px; align-items: flex-end;
        }
        .input-wrap { flex: 1; }
        .input-wrap textarea {
          width: 100%;
          background: rgba(10,24,48,0.95);
          border: 1px solid rgba(125,211,252,0.14);
          border-radius: 14px;
          padding: 11px 16px;
          font-size: 14px;
          font-family: 'DM Sans', sans-serif;
          color: #e2e8f0; resize: none; outline: none;
          height: 46px; max-height: 120px;
          overflow-y: auto; line-height: 1.5;
          transition: border-color 0.2s, box-shadow 0.2s;
        }
        .input-wrap textarea::placeholder { color: #334155; }
        .input-wrap textarea:focus { border-color: rgba(14,165,233,0.4); box-shadow: 0 0 0 3px rgba(14,165,233,0.07); }

        .send-btn {
          width: 46px; height: 46px; border-radius: 12px; border: none;
          background: linear-gradient(135deg, #0ea5e9, #0369a1);
          color: #fff; cursor: pointer;
          display: flex; align-items: center; justify-content: center;
          flex-shrink: 0;
          transition: all 0.2s;
          box-shadow: 0 0 14px rgba(14,165,233,0.25);
        }
        .send-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 0 22px rgba(14,165,233,0.45); }
        .send-btn:disabled { opacity: 0.3; cursor: not-allowed; box-shadow: none; }

        .footer-note {
          text-align: center; font-size: 10.5px; color: #1e3a5f;
          padding: 5px 0 8px; background: rgba(5,14,28,0.94);
          font-weight: 300; flex-shrink: 0; z-index: 20;
        }

        @keyframes fadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }

        @keyframes floatDrop {
          0%{transform:translateY(0) scale(1)} 50%{transform:translateY(-26px) scale(1.04)} 100%{transform:translateY(0) scale(1)}
        }

        @keyframes cursorBlink { 0%,100%{opacity:1} 50%{opacity:0} }

        /* Scrollbar */
        .messages::-webkit-scrollbar { width: 5px; }
        .messages::-webkit-scrollbar-track { background: transparent; }
        .messages::-webkit-scrollbar-thumb { background: rgba(125,211,252,0.12); border-radius: 3px; }

        /* Sidebar overlay on mobile */
        @media (max-width: 768px) {
          .sidebar-overlay { display: block !important; }
        }
      `}</style>

      <div className="app-shell">
        <WaterDrops />

        {/* Sidebar */}
        <Sidebar
          chats={chats}
          activeChatId={activeChatId}
          onSelect={id => { setActiveChatId(id); if (window.innerWidth <= 768) setSidebarCollapsed(true) }}
          onNew={newChat}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(v => !v)}
        />

        {/* Main panel */}
        <div className="main-panel">

          {/* Header */}
          <div className="header">
            <button className="toggle-btn" onClick={() => setSidebarCollapsed(v => !v)} title="Toggle sidebar">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
              </svg>
            </button>
            <div className="header-logo">
              <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" width="20" height="20">
                <path d="M12 2C6 2 2 8.5 2 13a10 10 0 0020 0c0-4.5-4-11-10-11z"/>
                <path d="M12 22v-6M9 19l3 3 3-3" opacity="0.5"/>
              </svg>
            </div>
            <div>
              <div className="header-name">INGRES Groundwater AI</div>
              <div className="header-sub">Central Ground Water Board · India</div>
            </div>
            <div className="header-pill">
              <div className="pulse-dot" />
              Live
            </div>
          </div>

          {/* Messages */}
          <div className="messages">
            <div className="messages-inner">
              {messages.length === 0 && (
                <div className="welcome">
                  <span className="welcome-icon">💧</span>
                  <div className="welcome-title">Ask me about groundwater</div>
                  <div className="welcome-sub">
                    Query rainfall, recharge levels, extraction rates, and water availability across India's states and districts.
                  </div>
                  <div className="chips">
                    {SUGGESTIONS.map((s, i) => (
                      <button key={i} className="chip" onClick={() => send(s)}>{s}</button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg) => (
                <div key={msg.id} className={`msg-row ${msg.role}`} style={{ marginBottom: 4 }}>
                  <div className={`avatar ${msg.role}`}>{msg.role === "user" ? "You" : "AI"}</div>
                  <div className={`bubble ${msg.role}`}>
                    {msg.role === "bot"
                      ? <BotMessage text={msg.text} animate={msg.animate} />
                      : <span style={{ whiteSpace: "pre-wrap" }}>{msg.text}</span>
                    }
                  </div>
                </div>
              ))}

              {loading && (
                <div className="msg-row bot">
                  <div className="avatar bot">AI</div>
                  <div className="bubble bot">
                    <div className="typing-dots">
                      <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          </div>

          {/* Input */}
          <div className="input-area">
            <div className="input-inner">
              <div className="input-wrap">
                <textarea
                  ref={textareaRef}
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  onKeyDown={handleKey}
                  placeholder="Ask about groundwater data across India…"
                  rows={1}
                />
              </div>
              <button className="send-btn" onClick={() => send()} disabled={loading || !question.trim()}>
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              </button>
            </div>
          </div>
          <div className="footer-note">INGRES · Ministry of Jal Shakti · Data: CGWB</div>
        </div>
      </div>
    </>
  )
}