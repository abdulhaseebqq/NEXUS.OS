import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import LoginPage from "./pages/auth/LoginPage"
import SignupPage from "./pages/auth/SignupPage"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />

        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App