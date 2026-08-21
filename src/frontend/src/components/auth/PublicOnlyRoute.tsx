import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"

import { useAuth } from "../../hooks/useAuth"

type PublicOnlyRouteProps = {
  children: ReactNode
}

function PublicOnlyRoute({
  children,
}: PublicOnlyRouteProps) {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  return children
}

export default PublicOnlyRoute