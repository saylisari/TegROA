import { useEffect, useState } from 'react'
import './App.css'

export default function App() {
  const [stats, setStats] = useState(null)
  const [events, setEvents] = useState([])
  const [alerts, setAlerts] = useState([])
  const [aiPredictions, setAiPredictions] = useState([])

  const [error, setError] = useState('')
  const [updated, setUpdated] = useState('')
  const [monitoring, setMonitoring] = useState(null)
  const [monitorBusy, setMonitorBusy] = useState(false)
  const [monitorError, setMonitorError] = useState('')

  async function loadData() {
    try {
      const responses = await Promise.all([
        fetch('http://127.0.0.1:8000/api/stats'),
        fetch('http://127.0.0.1:8000/api/events'),
        fetch('http://127.0.0.1:8000/api/alerts'),
        fetch('http://127.0.0.1:8000/api/monitoring/status'),
        fetch('http://127.0.0.1:8000/api/ai/predictions'),
      ])

      if (responses.some(response => !response.ok)) {
        throw new Error('Backend returned an error')
      }

      const [statsData, eventsData, alertsData, monitoringData, aiData] =
        await Promise.all(responses.map(response => response.json()))

      setStats(statsData)
      setEvents(eventsData)
      setAlerts(alertsData)
      setMonitoring(monitoringData.running)
      setAiPredictions(aiData)
      setUpdated(new Date().toLocaleTimeString())
      setError('')
    } catch {
      setError('Unable to connect to TegROA backend')
    }
  }

  async function controlMonitoring(action) {
    setMonitorBusy(true)
    setMonitorError('')

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/monitoring/${action}`,
        { method: 'POST' }
      )

      const result = await response.json()

      if (!response.ok || result.status === 'error') {
        throw new Error(result.message || 'Monitoring request failed')
      }

      await loadData()
    } catch (err) {
      setMonitorError(err.message)
    } finally {
      setMonitorBusy(false)
    }
  }

  useEffect(() => {
    loadData()
    const timer = setInterval(loadData, 5000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">T</div>
          <div>
            <h2>TegROA</h2>
            <span>SECURITY PLATFORM</span>
          </div>
        </div>

        <nav>
          <div className="nav-item active">◈ Overview</div>
          <div className="nav-item">◎ Network Events</div>
          <div className="nav-item">⚠ Security Alerts</div>
          <div className="nav-item">▤ System Status</div>
        </nav>

        <div className="sidebar-footer">
          TegROA v0.1.0
          <small>Security Monitoring Platform</small>
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <div className="eyebrow">SECURITY OPERATIONS CENTER</div>
            <h1>Security Overview</h1>
            <p>Network threat detection and monitoring</p>
          </div>
          <div className="header-actions">
            <span className={`status ${error ? 'offline' : ''}`}>
              ● {error ? 'Backend Offline' : stats ? 'System Online' : 'Connecting'}
            </span>
            <span className={`status ${monitoring ? '' : 'offline'}`}>
              ● Monitor {monitoring === null ? 'Unknown' : monitoring ? 'Running' : 'Stopped'}
            </span>
            <button
              onClick={() => controlMonitoring('start')}
              disabled={monitorBusy || monitoring !== false}
            >
              Start Monitoring
            </button>
            <button
              onClick={() => controlMonitoring('stop')}
              disabled={monitorBusy || monitoring !== true}
            >
              Stop Monitoring
            </button>
            <button onClick={loadData}>↻ Refresh</button>
          </div>
        </header>

        {error && <div className="error">{error}</div>}
        {monitorError && <div className="error">{monitorError}</div>}

        <section className="metrics">
          <div className="metric">
            <span>NETWORK EVENTS</span>
            <strong>{stats?.total_events ?? '—'}</strong>
            <small>Stored traffic records</small>
          </div>
          <div className="metric">
            <span>SECURITY ALERTS</span>
            <strong>{stats?.active_incidents ?? '-'}</strong>
            <small>Recent detected alerts</small>
          </div>
          <div className="metric">
            <span>CRITICAL ALERTS</span>
            <strong>{stats?.critical_alerts ?? '—'}</strong>
            <small>High-priority threats</small>
          </div>
          <div className="metric">
            <span>DATABASE STATUS</span>
            <strong className="database-status">
              {stats?.monitoring_status === 'database_ready' ? 'READY' : '—'}
            </strong>
            <small>PostgreSQL monitoring storage</small>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <h3>Security Alerts</h3>
              <p>Detected suspicious network activity</p>
            </div>
            <span className="panel-count">{stats?.active_incidents ?? alerts.length} total alerts</span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>DETECTION</th>
                  <th>SEVERITY</th>
                  <th>DESCRIPTION</th>
                </tr>
              </thead>
              <tbody>
                {alerts.length === 0 ? (
                  <tr><td colSpan="4">No alerts recorded</td></tr>
                ) : alerts.map(alert => (
                  <tr key={alert.id}>
                    <td>#{alert.id}</td>
                    <td>{alert.alert_type}</td>
                    <td>
                      <span className={`severity ${alert.severity}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td>{alert.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <h3>AI Predictions</h3>
              <p>Random Forest network flow classification</p>
            </div>
            <span className="panel-count">{stats?.total_ai_predictions ?? aiPredictions.length} total predictions</span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>SOURCE IP</th>
                  <th>DESTINATION IP</th>
                  <th>PORT</th>
                  <th>PREDICTION</th>
                  <th>CONFIDENCE</th>
                </tr>
              </thead>
              <tbody>
                {aiPredictions.length === 0 ? (
                  <tr><td colSpan="6">No AI predictions recorded</td></tr>
                ) : aiPredictions.map(item => (
                  <tr key={item.id}>
                    <td>#{item.id}</td>
                    <td>{item.source_ip}</td>
                    <td>{item.destination_ip}</td>
                    <td>{item.destination_port}</td>
                    <td>{item.prediction}</td>
                    <td>{(item.confidence * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <h3>Recent Network Events</h3>
              <p>Captured and imported packet metadata</p>
            </div>
            <span className="panel-count">{stats?.total_events ?? events.length} total events</span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>SOURCE IP</th>
                  <th>DESTINATION IP</th>
                  <th>PORT</th>
                  <th>PROTOCOL</th>
                </tr>
              </thead>
              <tbody>
                {events.length === 0 ? (
                  <tr><td colSpan="5">No network events recorded</td></tr>
                ) : events.map(event => (
                  <tr key={event.id}>
                    <td>#{event.id}</td>
                    <td>{event.source_ip}</td>
                    <td>{event.destination_ip}</td>
                    <td>{event.destination_port}</td>
                    <td><span className="protocol">{event.protocol}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <footer>
          <span>TEGROA SECURITY MONITORING SYSTEM</span>
          <span>Last updated: {updated || 'Waiting for data'}</span>
        </footer>
      </main>
    </div>
  )
}
