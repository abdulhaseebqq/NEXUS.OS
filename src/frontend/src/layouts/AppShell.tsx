import { useState } from "react"
import { Outlet } from "react-router-dom"

import Sidebar from "../components/navigation/Sidebar"
import Topbar from "../components/navigation/Topbar"

function AppShell() {
  const [isSidebarOpen, setIsSidebarOpen] =
    useState(false)

  function openSidebar() {
    setIsSidebarOpen(true)
  }

  function closeSidebar() {
    setIsSidebarOpen(false)
  }

  return (
    <div className="app-shell">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={closeSidebar}
      />

      {isSidebarOpen && (
        <button
          type="button"
          className="sidebar-backdrop"
          aria-label="Close navigation"
          onClick={closeSidebar}
        />
      )}

      <div className="app-main">
        <Topbar
          onMenuClick={openSidebar}
        />

        <div className="app-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default AppShell