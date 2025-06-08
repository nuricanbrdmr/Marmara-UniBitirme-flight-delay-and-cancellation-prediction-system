import { Route, Routes } from "react-router-dom";
import Home from "./components/Home";
import TicketDetails from "./ticket/[id]/page";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Register from "./components/Register";
import Login from "./components/Login";
import PersistLogin from "./components/PersistentLogin";
import LoginControl from "./components/LoginControl";
import ResetPassword from "./components/ResetPassword";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route element={<PersistLogin />}>
          <Route element={<LoginControl />}>
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/resetPassword" element={<ResetPassword />} />
          </Route>
          <Route path="/" element={<Home />} />
          <Route path="/ticket/:id" element={<TicketDetails />} />
        </Route>
      </Routes>
      <Footer />
    </>
  );
}

export default App;
