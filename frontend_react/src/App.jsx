import { useState, useRef, useEffect, useCallback } from 'react'

const EXAMPLE_PROMPTS = [
  'วิเคราะห์หุ้น AAPL ให้หน่อย',
  'พอร์ตความเสี่ยงต่ำควรลงทุนอะไร?',
  'RSI กับ MACD ต่างกันอย่างไร?',
  'ทองคำกับหุ้นอะไรดีกว่าในช่วงนี้?',
]

const SESSION_ID = `session-${Math.random().toString(36).slice(2)}`
const USER_ID = 'user-demo-001'

function formatTime(ms) {
  if (ms == null) return '—'
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`
}

function formatCost(usd) {
  if (usd == null) return '—'
  if (usd === 0) return '$0.00 (free)'
  return usd < 0.001 ? `$${(usd * 1000).toFixed(4)}m` : `$${usd.toFixed(5)}`
}

export default function App() {
  const [mode, setMode] = useState('baseline') // 'baseline' | 'intent'
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [lastMeta, setLastMeta] = useState(null)
  const [showReport, setShowReport] = useState(false)
  const [reportData, setReportData] = useState(null)
  const [loadingReport, setLoadingReport] = useState(false)

  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const fetchReport = async () => {
    setLoadingReport(true)
    setShowReport(true)
    try {
      // The report API is under project 2 intent agent
      const res = await fetch('http://localhost:8802/investment-ai-agent-intent/report', { cache: 'no-store' })
      try {
        const data = await res.json()
        setReportData(data)
      } catch (e) {
        setReportData(null)
      }
    } catch (err) {
      console.error('Error fetching report', err)
    } finally {
      setLoadingReport(false)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Clear conversation when switching modes
  useEffect(() => {
    setMessages([])
    setLastMeta(null)
  }, [mode])

  const sendMessage = useCallback(async (text) => {
    const msgText = (text || input).trim()
    if (!msgText || loading) return

    setInput('')
    setLoading(true)

    const userMsg = { role: 'user', content: msgText, ts: Date.now() }
    setMessages(prev => [...prev, userMsg])

    try {
      const endpoint = mode === 'baseline'
        ? '/investment-ai-agent/chat'
        : '/investment-ai-agent-intent/chat'

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: SESSION_ID, user_id: USER_ID, message: msgText }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`)

      const data = await res.json()

      const botContent = mode === 'baseline' ? data.message : data.answer
      const botMsg = { role: 'bot', content: botContent, ts: Date.now() }
      setMessages(prev => [...prev, botMsg])

      // Extract metadata for analytics panel
      if (mode === 'baseline') {
        setLastMeta({
          mode: 'baseline',
          tokens: data.usage?.total_tokens,
          prompt_tokens: data.usage?.prompt_tokens,
          completion_tokens: data.usage?.completion_tokens,
          cost_usd: data.cost_usd,
          latency_ms: data.latency_ms,
        })
      } else {
        setLastMeta({
          mode: 'intent',
          tokens: data.usage?.total_tokens,
          prompt_tokens: data.usage?.prompt_tokens,
          completion_tokens: data.usage?.completion_tokens,
          cost_usd: data.billing?.cost_usd,
          cost_thb: data.billing?.cost_thb,
          latency_ms: data.latency_ms,
          intent: data.intent,
          selected_agent: data.selected_agent,
          selected_model: data.selected_model,
        })
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'bot',
        content: `⚠️ เกิดข้อผิดพลาด: ${err.message}\n\nกรุณาตรวจสอบว่า Backend กำลังทำงานอยู่บน port ${mode === 'baseline' ? '8801' : '8802'}`,
        ts: Date.now(),
        isError: true,
      }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, mode])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="logo-icon">📈</div>
          <h1>Dual-Agent Investment AI</h1>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button 
            onClick={fetchReport}
            style={{
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid var(--accent-blue)',
              color: 'var(--accent-blue)',
              padding: '0.4rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: 500
            }}
          >
            📊 View Report
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
            <div className="status-dot" />
            <span style={{ color: 'var(--text-muted)' }}>Systems Online</span>
          </div>
        </div>
      </header>

      {/* Report Modal */}
      {showReport && (() => {
        if (loadingReport) {
          return (
            <div className="modal-overlay" onClick={() => setShowReport(false)}>
              <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-body" style={{ textAlign: 'center', padding: '2rem' }}>
                  กำลังโหลดข้อมูล...
                </div>
              </div>
            </div>
          )
        }
        if (!reportData || (!reportData.overall && !reportData.error)) {
          return (
            <div className="modal-overlay" onClick={() => setShowReport(false)}>
              <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>📊 Token & Cost Report</h3>
                  <button className="close-btn" onClick={() => setShowReport(false)}>×</button>
                </div>
                <div className="modal-body" style={{ textAlign: 'center', padding: '2rem' }}>
                  <p style={{ color: 'var(--accent-amber)' }}>ไม่สามารถดึงข้อมูลได้</p>
                </div>
              </div>
            </div>
          )
        }

        if (reportData.error) {
          return (
            <div className="modal-overlay" onClick={() => setShowReport(false)}>
              <div className="modal-content" onClick={e => e.stopPropagation()} style={{maxWidth: '800px'}}>
                <div className="modal-header">
                  <h3>📊 Token & Cost Report (ERROR)</h3>
                  <button className="close-btn" onClick={() => setShowReport(false)}>×</button>
                </div>
                <div className="modal-body" style={{ textAlign: 'left', padding: '2rem', overflowX: 'auto' }}>
                  <p style={{ color: 'var(--accent-amber)' }}>Backend Error: {reportData.error}</p>
                  <pre style={{ fontSize: '0.75rem', color: '#ffaaaa', marginTop: '1rem', whiteSpace: 'pre-wrap' }}>{reportData.traceback}</pre>
                </div>
              </div>
            </div>
          )
        }

        return (
          <div className="modal-overlay" onClick={() => setShowReport(false)}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
              <div className="modal-header">
                <div className="modal-title">📊 Token & Cost Report</div>
                <button className="close-btn" onClick={() => setShowReport(false)}>×</button>
              </div>
              <div className="modal-body">
                <>
                  <div className="report-section">
                    <h4>ภาพรวมทั้งหมด (Overall)</h4>
                    <div className="metric-grid" style={{ marginBottom: '1rem' }}>
                      <div className="metric-card">
                        <div className="metric-label">Total Tokens Used</div>
                        <div className="metric-value blue">{reportData.overall.total_tokens.toLocaleString()}</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-label">Total Cost</div>
                        <div className="metric-value green">
                          ${reportData.overall.total_cost_usd.toFixed(5)}
                          <div className="metric-unit">≈ ฿{reportData.overall.total_cost_thb.toFixed(2)}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="report-section">
                    <h4>แยกตามโปรเจกต์ (By Project)</h4>
                    <table className="report-table">
                      <thead>
                        <tr>
                          <th>Project Name</th>
                          <th>Requests</th>
                          <th>Tokens</th>
                          <th>Cost (USD)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reportData.by_project.map((p, i) => (
                          <tr key={i}>
                            <td>
                              <span className={`tag ${p.project_name.includes('intent') ? 'tag-purple' : 'tag-blue'}`}>
                                {p.project_name === 'project_1_baseline' ? 'Baseline (🤖)' : 'Intent (🧠)'}
                              </span>
                            </td>
                            <td>{p.total_requests.toLocaleString()}</td>
                            <td>{p.total_tokens.toLocaleString()}</td>
                            <td className="green">${p.cost_usd.toFixed(5)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="report-section">
                    <h4>20 รายการล่าสุด (Recent Transactions)</h4>
                    <div style={{ maxHeight: '250px', overflowY: 'auto', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
                      <table className="report-table" style={{ border: 'none', borderRadius: 0 }}>
                        <thead style={{ position: 'sticky', top: 0, zIndex: 1, background: 'var(--bg-secondary)' }}>
                          <tr>
                            <th>เวลา</th>
                            <th>โมเดล</th>
                            <th>Tokens</th>
                            <th>ค่าใช้จ่าย (฿)</th>
                          </tr>
                        </thead>
                        <tbody>
                          {reportData.recent_transactions?.map((t, i) => (
                            <tr key={i}>
                              <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                {new Date(t.created_at).toLocaleString('th-TH', { 
                                  month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' 
                                })}
                              </td>
                              <td>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                  <span className={`tag ${(t.project_name || '').includes('intent') ? 'tag-purple' : 'tag-blue'}`} style={{ alignSelf: 'flex-start', fontSize: '0.65rem' }}>
                                    {t.project_name === 'project_1_baseline' ? 'Baseline' : 'Intent'}
                                  </span>
                                  <span style={{ fontSize: '0.75rem' }}>{(t.model || 'Unknown').replace('google/', '')}</span>
                                </div>
                              </td>
                              <td className="blue">{t.tokens.toLocaleString()}</td>
                              <td className="amber">฿{t.cost_thb.toFixed(4)}</td>
                            </tr>
                          ))}
                          {(!reportData.recent_transactions || reportData.recent_transactions.length === 0) && (
                            <tr>
                              <td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '1rem' }}>
                                ยังไม่มีข้อมูลการใช้งาน
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              </div>
            </div>
          </div>
        )
      })()}

      {/* Main */}
      <div className="main-layout">
        {/* Mode Selector */}
        <div className="mode-selector">
          <button
            id="btn-baseline"
            className={`mode-btn ${mode === 'baseline' ? 'active' : ''}`}
            onClick={() => setMode('baseline')}
          >
            <span>🤖</span>
            <div>
              <div>Baseline Agent</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Single LLM · Large Prompt</div>
            </div>
            <span className="mode-badge badge-baseline">Project 1</span>
          </button>
          <button
            id="btn-intent"
            className={`mode-btn ${mode === 'intent' ? 'active-intent' : ''}`}
            onClick={() => setMode('intent')}
          >
            <span>🧠</span>
            <div>
              <div>Intent Optimized</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Multi-Agent · Dynamic Routing</div>
            </div>
            <span className="mode-badge badge-intent">Project 2</span>
          </button>
        </div>

        {/* Chat Panel */}
        <div className="chat-panel">
          <div className="chat-messages">
            {messages.length === 0 && !loading ? (
              <div className="empty-state">
                <div className="empty-icon">💬</div>
                <h3>เริ่มต้นถามเกี่ยวกับการลงทุน</h3>
                <p style={{ fontSize: '0.83rem' }}>ลองถามเกี่ยวกับหุ้น, พอร์ตโฟลิโอ, หรือกลยุทธ์การลงทุน</p>
                <div className="example-prompts">
                  {EXAMPLE_PROMPTS.map((p, i) => (
                    <button key={i} className="example-chip" onClick={() => sendMessage(p)}>{p}</button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, i) => (
                  <div key={i} className={`message ${msg.role}`}>
                    <div className={`msg-avatar ${msg.role === 'user' ? 'user-av' : 'bot-av'}`}>
                      {msg.role === 'user' ? '👤' : msg.role === 'bot' && msg.isError ? '⚠️' : '🤖'}
                    </div>
                    <div>
                      <div className="msg-bubble" style={msg.isError ? { borderColor: 'rgba(239,68,68,0.4)', background: 'rgba(239,68,68,0.05)' } : {}}>
                        {msg.content}
                      </div>
                      <div className="msg-meta">
                        {new Date(msg.ts).toLocaleTimeString('th-TH')}
                      </div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="message bot">
                    <div className="msg-avatar bot-av">🤖</div>
                    <div className="msg-bubble">
                      <div className="typing-indicator">
                        <div className="typing-dot" />
                        <div className="typing-dot" />
                        <div className="typing-dot" />
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input-area">
            <div className="input-row">
              <textarea
                id="chat-input"
                ref={textareaRef}
                className="chat-input"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="พิมพ์คำถามเกี่ยวกับการลงทุน... (Enter เพื่อส่ง)"
                rows={1}
                disabled={loading}
              />
              <button
                id="send-btn"
                className="send-btn"
                onClick={() => sendMessage()}
                disabled={!input.trim() || loading}
                title="ส่งข้อความ"
              >
                ➤
              </button>
            </div>
          </div>
        </div>

        {/* Analytics Panel */}
        <div className="analytics-panel">
          <p className="analytics-title">📊 Analytics &amp; Metrics</p>

          {!lastMeta ? (
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '2rem 0' }}>
              ส่งข้อความเพื่อดู metrics
            </div>
          ) : (
            <>
              <div className="metric-grid">
                <div className="metric-card">
                  <div className="metric-label">Total Tokens</div>
                  <div className="metric-value blue">
                    {lastMeta.tokens?.toLocaleString() ?? '—'}
                    <span className="metric-unit"> tok</span>
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Latency</div>
                  <div className="metric-value amber">
                    {formatTime(lastMeta.latency_ms)}
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Prompt Tokens</div>
                  <div className="metric-value" style={{ fontSize: '1.2rem' }}>
                    {lastMeta.prompt_tokens?.toLocaleString() ?? '—'}
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Completion Tokens</div>
                  <div className="metric-value" style={{ fontSize: '1.2rem' }}>
                    {lastMeta.completion_tokens?.toLocaleString() ?? '—'}
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-label">Cost (USD)</div>
                <div className="metric-value green" style={{ fontSize: '1.3rem' }}>
                  {formatCost(lastMeta.cost_usd)}
                </div>
                {lastMeta.cost_thb != null && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    ≈ ฿{lastMeta.cost_thb?.toFixed(4)} THB
                  </div>
                )}
              </div>

              {lastMeta.mode === 'intent' && lastMeta.intent && (
                <>
                  <p className="analytics-title">🧠 Intent Classification</p>
                  <div className="intent-card">
                    <div className="intent-row">
                      <span className="intent-key">Domain</span>
                      <span className="intent-val">
                        <span className="tag tag-purple">{lastMeta.intent.domain ?? '—'}</span>
                      </span>
                    </div>
                    <div className="intent-row">
                      <span className="intent-key">Complexity</span>
                      <span className="intent-val">
                        <span className="tag tag-blue">{lastMeta.intent.complexity ?? '—'}</span>
                      </span>
                    </div>
                    <div className="intent-row">
                      <span className="intent-key">Selected Agent</span>
                      <span className="intent-val">{lastMeta.selected_agent ?? '—'}</span>
                    </div>
                    <div className="intent-row">
                      <span className="intent-key">Selected Model</span>
                      <span className="intent-val" style={{ fontSize: '0.75rem', wordBreak: 'break-all' }}>
                        {lastMeta.selected_model ?? '—'}
                      </span>
                    </div>
                    {lastMeta.intent.ticker && (
                      <div className="intent-row">
                        <span className="intent-key">Ticker</span>
                        <span className="intent-val">
                          <span className="tag tag-green">{lastMeta.intent.ticker}</span>
                        </span>
                      </div>
                    )}
                    {lastMeta.intent.reason && (
                      <div style={{ marginTop: '0.75rem', padding: '0.625rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        💡 {lastMeta.intent.reason}
                      </div>
                    )}
                  </div>
                </>
              )}

              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '0.875rem',
                fontSize: '0.78rem',
                color: 'var(--text-muted)',
                marginTop: 'auto',
              }}>
                <span style={{ color: 'var(--accent-amber)' }}>⚡ Mode: </span>
                {lastMeta.mode === 'baseline' ? 'Baseline (Single LLM)' : 'Intent Optimized (Multi-Agent)'}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  )
}
