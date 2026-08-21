import { useNavigate } from "react-router-dom"

import { useAuth } from "../../hooks/useAuth"

function DashboardPage() {
  const navigate = useNavigate()

  const {
    user,
    logout,
  } = useAuth()

  function handleLogout() {
    logout()

    navigate("/login", {
      replace: true,
    })
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <span className="auth-badge">
            NEXUS.OS
          </span>

          <h1>
            Welcome,{" "}
            {user?.full_name ??
              user?.email ??
              "User"}
          </h1>

          <p>
            Your authenticated NEXUS.OS workspace is ready.
          </p>
        </div>

        <div className="verification-email">
          <span>Signed in as</span>

          <strong>
            {user?.email}
          </strong>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={handleLogout}
        >
          Log out
        </button>
      </section>
    </main>
  )
}

export default DashboardPage