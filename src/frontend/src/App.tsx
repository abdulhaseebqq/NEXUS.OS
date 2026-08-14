import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom"

import LoginPage from "./pages/auth/LoginPage"
import SignupPage from "./pages/auth/SignupPage"
import VerifyEmailPage from "./pages/auth/VerifyEmailPage"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Navigate
              to="/login"
              replace
            />
          }
        />

        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/signup"
          element={<SignupPage />}
        />

        <Route
          path="/verify-email"
          element={<VerifyEmailPage />}
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App