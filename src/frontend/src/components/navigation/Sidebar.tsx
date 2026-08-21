import {
  FaBrain,
  FaComments,
  FaCog,
  FaHome,
  FaSignOutAlt,
  FaUser,
} from "react-icons/fa"
import {
  NavLink,
  useNavigate,
} from "react-router-dom"

import { useAuth } from "../../hooks/useAuth"

type SidebarProps = {
  isOpen: boolean
  onClose: () => void
}

function Sidebar({
  isOpen,
  onClose,
}: SidebarProps) {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  function handleLogout() {
    logout()

    navigate("/login", {
      replace: true,
    })
  }

  return (
    <aside
      className={
        isOpen
          ? "app-sidebar app-sidebar-open"
          : "app-sidebar"
      }
    >
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          N
        </div>

        <div>
          <strong>NEXUS.OS</strong>
          <span>AI Operating System</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/dashboard"
          onClick={onClose}
          className={({ isActive }) =>
            isActive
              ? "sidebar-link sidebar-link-active"
              : "sidebar-link"
          }
        >
          <FaHome />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/chat"
          onClick={onClose}
          className={({ isActive }) =>
            isActive
              ? "sidebar-link sidebar-link-active"
              : "sidebar-link"
          }
        >
          <FaComments />
          <span>AI Chat</span>
        </NavLink>

        <button
          type="button"
          className="sidebar-link sidebar-disabled"
          disabled
        >
          <FaBrain />
          <span>Memory</span>
          <small>Soon</small>
        </button>

        <NavLink
          to="/profile"
          onClick={onClose}
          className={({ isActive }) =>
            isActive
              ? "sidebar-link sidebar-link-active"
              : "sidebar-link"
          }
        >
          <FaUser />
          <span>Profile</span>
        </NavLink>

        <NavLink
          to="/settings"
          onClick={onClose}
          className={({ isActive }) =>
            isActive
              ? "sidebar-link sidebar-link-active"
              : "sidebar-link"
          }
        >
          <FaCog />
          <span>Settings</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">
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
              {user?.email}
            </span>
          </div>
        </div>

        <button
          type="button"
          className="sidebar-logout"
          onClick={handleLogout}
        >
          <FaSignOutAlt />
          <span>Log out</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar