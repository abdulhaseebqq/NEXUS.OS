import {
  FaBrain,
  FaComments,
  FaDesktop,
  FaMobileAlt,
} from "react-icons/fa"
import { Link } from "react-router-dom"

import { useAuth } from "../../hooks/useAuth"

function DashboardPage() {
  const { user } = useAuth()

  return (
    <main className="dashboard-view">
      <section className="dashboard-hero">
        <div>
          <span className="dashboard-kicker">
            SYSTEM ONLINE
          </span>

          <h1>
            Welcome back,{" "}
            {user?.full_name ??
              user?.email}
          </h1>

          <p>
            Your NEXUS.OS command center is ready.
            Start a conversation or continue building
            your connected AI workspace.
          </p>
        </div>

        <Link
          to="/chat"
          className="dashboard-primary-action"
        >
          Open NEXUS AI
        </Link>
      </section>

      <section className="dashboard-stats">
        <article className="dashboard-stat-card">
          <FaComments />

          <div>
            <strong>AI Chat</strong>
            <span>Ready</span>
          </div>
        </article>

        <article className="dashboard-stat-card">
          <FaBrain />

          <div>
            <strong>Memory</strong>
            <span>Coming next</span>
          </div>
        </article>

        <article className="dashboard-stat-card">
          <FaDesktop />

          <div>
            <strong>Desktop</strong>
            <span>Planned</span>
          </div>
        </article>

        <article className="dashboard-stat-card">
          <FaMobileAlt />

          <div>
            <strong>Mobile Sync</strong>
            <span>Planned</span>
          </div>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="dashboard-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>QUICK START</span>
              <h2>Ask NEXUS anything</h2>
            </div>

            <FaComments />
          </div>

          <p>
            The next sprint connects this workspace
            to the real AI conversation engine.
          </p>

          <Link
            to="/chat"
            className="dashboard-secondary-action"
          >
            Go to AI Chat
          </Link>
        </article>

        <article className="dashboard-panel">
          <div className="dashboard-panel-header">
            <div>
              <span>ACCOUNT</span>
              <h2>Your workspace</h2>
            </div>
          </div>

          <div className="dashboard-account-row">
            <span>Email</span>
            <strong>{user?.email}</strong>
          </div>

          <div className="dashboard-account-row">
            <span>Status</span>
            <strong className="status-online">
              Active
            </strong>
          </div>

          <div className="dashboard-account-row">
            <span>Role</span>
            <strong>
              {user?.role ?? "user"}
            </strong>
          </div>
        </article>
      </section>
    </main>
  )
}

export default DashboardPage