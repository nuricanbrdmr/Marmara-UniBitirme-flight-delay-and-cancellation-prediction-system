import { useEffect, useState } from "react";
import useAuth from "../hooks/useAuth";
import { Outlet, useNavigate } from "react-router-dom";
import { Spin } from "antd";

const LoginControl = () => {
    const [yukleniyor, setYukleniyor] = useState(false);
    const { auth } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        setYukleniyor(true);
        if (auth.accessToken) {
            navigate("/");
        }
        setYukleniyor(false);
    }, [auth])

    return <>{yukleniyor ? <Spin /> : <Outlet />}</>;
}

export default LoginControl