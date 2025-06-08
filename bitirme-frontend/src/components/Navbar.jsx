import { Link } from "react-router-dom";
import { FaUserAlt } from "react-icons/fa";
import { RiLogoutBoxLine } from "react-icons/ri";
import { useState } from "react";
import useAuth from "../hooks/useAuth";
import useLogout from "../hooks/useLogout";

const Navbar = () => {
  const [isHovered, setIsHovered] = useState(false);
  const { auth } = useAuth();
  const logout = useLogout();
  return (
    <header className="w-full fixed px-10 sm:px-10 md:px-10 lg:px-24 xl:px-52 z-50 shadow-lg">
      <nav className="flex justify-between items-center w-full max-sm:gap-5">
        <Link to={"/"}>
          <span
            style={{ textShadow: "2px 2px 4px rgba(0, 0, 0, 0.7)" }}
            className="font-extrabold font-mono text-[34px] max-sm:text-[22px] text-white"
          >
            Smart<span className="text-red-600">Ticket</span>
          </span>
        </Link>
        <div
          className="gap-5 flex py-3 justify-center items-center text-white font-semibold"
          style={{ textShadow: "2px 2px 4px rgba(0, 0, 0, 0.7)" }}
        >
          {auth.accessToken ? (
            <span
              onClick={logout}
              className="flex justify-center cursor-pointer items-center gap-2 font-bold  
                        bg-[#3f3f3f] bg-opacity-50 hover:bg-opacity-100 py-2 px-4 rounded-full"
            >
              <RiLogoutBoxLine
                size={18}
                className="text-white group-hover:text-gray-200"
              />
              Logout
            </span>
          ) : (
            <>
              <Link to={"/register"}>
                <span
                  className="cursor-pointer group"
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                >
                  Register
                </span>
              </Link>
              <Link to={"/login"}>
                <span
                  className="flex justify-center cursor-pointer items-center gap-2 font-bold  
                         bg-[#3f3f3f] bg-opacity-50 hover:bg-opacity-100 py-2 px-4 rounded-full"
                >
                  Login
                  <FaUserAlt className="text-white group-hover:text-gray-200" />
                </span>
              </Link>
            </>
          )}
        </div>
      </nav>
      {isHovered && (
        <div className="relative w-full">
          <span className="absolute right-[117px] w-[62px] h-[3px] top-0 bg-[#3f3f3f]"></span>
        </div>
      )}
    </header>
  );
};

export default Navbar;
