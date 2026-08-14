import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"

import { verifyEmail } from "../../services/auth"
import { ApiRequestError } from "../../services/api"

function VerifyEmailPage() {
  const navigate = useNavigate()

  const [error, setError] = useState("")
  const [successMessage, setSuccessMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const verificationToken =
    sessionStorage.getItem(
      "nexus_email_verification_token",
    )

  const verificationEmail =
    sessionStorage.getItem(
      "nexus_verification_email",
    )

  async function handleVerifyEmail() {
    setError("")
    setSuccessMessage("")

    if (!verificationToken) {
      setError(
        "Verification token is missing. Please create your account again.",
      )
      return
    }

    try {
      setIsLoading(true)

      const response = await verifyEmail({
        token: verificationToken,
      })

      setSuccessMessage(response.message)

      sessionStorage.removeItem(
        "nexus_email_verification_token",
      )

      sessionStorage.removeItem(
        "nexus_verification_email",
      )

      window.setTimeout(() => {
        navigate("/login", {
          replace: true,
        })
      }, 1200)
    } catch (caughtError) {
      if (caughtError instanceof ApiRequestError) {
        setError(caughtError.message)
        return
      }

      setError(
        "Unable to verify your email. Please try again.",
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <span className="auth-badge">
            NEXUS.OS
          </span>

          <h1>Verify your email</h1>

          <p>
            Your account has been created. Verify your
            email before signing in.
          </p>
        </div>

        {verificationEmail && (
          <div className="verification-email">
            <span>Account email</span>
            <strong>{verificationEmail}</strong>
          </div>
        )}

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}

        {successMessage && (
          <p
            className="form-success"
            role="status"
          >
            {successMessage}
            {" Redirecting to login..."}
          </p>
        )}

        <button
          type="button"
          className="primary-button verification-button"
          onClick={handleVerifyEmail}
          disabled={
            isLoading ||
            Boolean(successMessage)
          }
        >
          {isLoading
            ? "Verifying..."
            : successMessage
              ? "Verified"
              : "Verify email"}
        </button>

        <p className="auth-switch">
          Already verified?{" "}
          <Link to="/login">
            Sign in
          </Link>
        </p>
      </section>
    </main>
  )
}

export default VerifyEmailPage