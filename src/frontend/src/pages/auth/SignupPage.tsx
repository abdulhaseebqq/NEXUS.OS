import { useState } from "react"
import type { FormEvent } from "react"
import { FaGithub, FaGoogle, FaMicrosoft } from "react-icons/fa"
import { Link } from "react-router-dom"

function SignupPage() {
  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false)
  const [error, setError] = useState("")

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")

    const normalizedName = fullName.trim()
    const normalizedEmail = email.trim()

    if (normalizedName.length < 2) {
      setError("Full name must be at least 2 characters.")
      return
    }

    if (normalizedName.length > 100) {
      setError("Full name must not exceed 100 characters.")
      return
    }

    if (!normalizedEmail) {
      setError("Email is required.")
      return
    }

    if (!normalizedEmail.includes("@")) {
      setError("Enter a valid email address.")
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

    if (password !== confirmPassword) {
      setError("Passwords do not match.")
      return
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <span className="auth-badge">NEXUS.OS</span>

          <h1>Create your account</h1>

          <p>
            Start building your secure personal AI workspace.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Full name

            <input
              type="text"
              value={fullName}
              onChange={(event) =>
                setFullName(event.target.value)
              }
              placeholder="Your full name"
              autoComplete="name"
              maxLength={100}
            />
          </label>

          <label>
            Email

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
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
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Minimum 8 characters"
                autoComplete="new-password"
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

          <label>
            Confirm password

            <div className="password-field">
              <input
                type={
                  showConfirmPassword
                    ? "text"
                    : "password"
                }
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Repeat your password"
                autoComplete="new-password"
                maxLength={128}
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowConfirmPassword((value) => !value)
                }
                aria-label={
                  showConfirmPassword
                    ? "Hide confirm password"
                    : "Show confirm password"
                }
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            </div>
          </label>

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <button className="primary-button" type="submit">
            Create account
          </button>
        </form>

        <div className="social-divider">
          <span>or sign up with</span>
        </div>

        <div className="social-login-grid">
          <button
            type="button"
            className="social-login-button"
            aria-label="Sign up with Google"
          >
            <FaGoogle className="social-real-icon google-real-icon" />
            <span>Google</span>
          </button>

          <button
            type="button"
            className="social-login-button"
            aria-label="Sign up with GitHub"
          >
            <FaGithub className="social-real-icon github-real-icon" />
            <span>GitHub</span>
          </button>

          <button
            type="button"
            className="social-login-button"
            aria-label="Sign up with Microsoft"
          >
            <FaMicrosoft className="social-real-icon microsoft-real-icon" />
            <span>Microsoft</span>
          </button>
        </div>

        <p className="auth-switch">
          Already have an account?{" "}
          <Link to="/login">
            Sign in
          </Link>
        </p>
      </section>
    </main>
  )
}

export default SignupPage