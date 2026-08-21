import {
  FaBars,
  FaBell,
} from "react-icons/fa"

import { useAuth } from "../../hooks/useAuth"

type TopbarProps = {
  onMenuClick: () => void
}

function Topbar({
  onMenuClick,
}: TopbarProps) {
  const { user } = useAuth()

  return (
    <header className="app-topbar">
      <div className="topbar-left">
        <button
          type="button"
          className="mobile-menu-button"
          aria-label="Open navigation"
          onClick={onMenuClick}
        >
          <FaBars />
        </button>

        <div>
          <span className="topbar-eyebrow">
            NEXUS.OS
          </span>

          <strong>
            Command Center
          </strong>
        </div>
      </div>

      <div className="topbar-actions">
        <button
          type="button"
          className="topbar-icon-button"
          aria-label="Notifications"
        >
          <FaBell />
        </button>

        <div className="topbar-user">
          <div className="topbar-avatar">
            {(
              user?.full_name ??
              user?.email ??
              "U"
            )
              .charAt(0)
              .toUpperCase()}
          </div>

          <div>
            <strong>
              {user?.full_name ??
                "NEXUS User"}
            </strong>

            <span>
              {user?.role ??
                "user"}
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Topbar