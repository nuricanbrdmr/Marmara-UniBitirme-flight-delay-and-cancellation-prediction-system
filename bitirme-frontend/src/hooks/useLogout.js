import { message } from "antd";
import useAuth from "./useAuth";
import Cookies from "js-cookie";

const useLogout = () => {
    const { setAuth } = useAuth();
    const logout = async () => {
        setAuth({});
        localStorage.setItem("persist", false)
        Cookies.remove("refreshToken")
        message.success("Exit Process Successful.")
    };

    return logout;
};

export default useLogout;