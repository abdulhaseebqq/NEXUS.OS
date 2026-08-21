import { useAuth } from "../../hooks/useAuth"

function ProfilePage() {
  const { user } = useAuth()

  return (
    <main className="simple-page">
      <div className="simple-page-header">
        <span>ACCOUNT</span>
        <h1>Profile</h1>
        <p>
          Review your NEXUS.OS identity and account
          information.
        </p>
      </div>

      <section className="simple-card">
        <div className="profile-avatar-large">
          {(
            user?.full_name ??
            user?.email ??
            "U"
          )
            .charAt(0)
            .toUpperCase()}
        </div>

        <div className="profile-details">
          <div>
            <span>Full name</span>
            <strong>
              {user?.full_name ??
                "Not available"}
            </strong>
          </div>

          <div>
            <span>Email</span>
            <strong>
              {user?.email}
            </strong>
          </div>

          <div>
            <span>Role</span>
            <strong>
              {user?.role ??
                "user"}
            </strong>
          </div>

          <div>
            <span>Account status</span>
            <strong className="status-online">
              Active
            </strong>
          </div>
        </div>
      </section>
    </main>
  )
}

export default ProfilePage