import { useState } from "react"
import type { FormEvent } from "react"
import { FaGithub, FaGoogle, FaMicrosoft } from "react-icons/fa"
import { Link } from "react-router-dom"

function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")

    const normalizedEmail = email.trim()

    if (!normalizedEmail) {
      setError("Email is required.")
      return
    }

    if (!normalizedEmail.includes("@")) {
      setError("Enter a valid email address.")
      return
    }

    if (!password) {
      setError("Password is required.")
      return
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.")
      return
    }

    if (password.length > 128) {
      setError("Password must not exceed 128 characters.")
      return
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <span className="auth-badge">NEXUS.OS</span>

          <h1>Welcome back</h1>

          <p>
            Sign in to continue to your secure NEXUS workspace.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email

            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              maxLength={254}
            />
          </label>

          <label>
            Password

            <div className="password-field">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                maxLength={128}
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword((value) => !value)
                }
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </label>

          <div className="auth-options">
            <label className="remember-option">
              <input type="checkbox" />
              <span>Remember me</span>
            </label>

            <button
              type="button"
              className="forgot-password"
            >
              Forgot password?
            </button>
          </div>

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <button className="primary-button" type="submit">
            Sign in
          </button>
        </form>

        <div className="social-divider">
          <span>or continue with</span>
        </div>

        <div className="social-login-grid">
          <button
            type="button"
            className="social-login-button"
            aria-label="Continue with Google"
          >
            <FaGoogle className="social-real-icon google-real-icon" />
            <span>Google</span>
          </button>

          <button
            type="button"
            className="social-login-button"
            aria-label="Continue with GitHub"
          >
            <FaGithub className="social-real-icon github-real-icon" />
            <span>GitHub</span>
          </button>

          <button
            type="button"
            className="social-login-button"
            aria-label="Continue with Microsoft"
          >
            <FaMicrosoft className="social-real-icon microsoft-real-icon" />
            <span>Microsoft</span>
          </button>
        </div>

        <p className="auth-switch">
          New to NEXUS.OS?{" "}
          <Link to="/signup">
            Create an account
          </Link>
        </p>
      </section>
    </main>
  )
}

export default LoginPage