import { Outlet, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import useRefreshToken from "../hooks/useRefreshToken";
import useAuth from "../hooks/useAuth";
import { Spin } from "antd";

const PersistLogin = () => {
    const [yukleniyor, setYukleniyor] = useState(false);
    const yenile = useRefreshToken();
    const { auth, persist } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        setYukleniyor(true);
        const tokenYenilemeDogrula = async () => {
            try {
                await yenile();
            } catch (err) {
                navigate("/login");
                console.error(err);
            }
        };
        if (persist && !auth.accessToken) {
            tokenYenilemeDogrula()
        }
        setYukleniyor(false);
    }, [auth])

    return <>{!persist ? <Outlet /> : yukleniyor ? <Spin /> : <Outlet />}</>;
};

export default PersistLogin;