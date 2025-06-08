import { createContext, useState, useEffect } from "react";
import PropTypes from "prop-types";

const AuthContext = createContext({
    auth: {},
    setAuth: () => { },
    persist: false,
    setPersist: () => { }
});

export const AuthProvider = ({ children }) => {
    const [auth, setAuth] = useState({});
    const [persist, setPersist] = useState(() => {
        const storedPersist = localStorage.getItem("persist");
        return storedPersist ? JSON.parse(storedPersist) : false;
    });

    useEffect(() => {
        localStorage.setItem("persist", JSON.stringify(persist));
    }, [persist]);

    return (
        <AuthContext.Provider value={{ auth, setAuth, persist, setPersist }}>
            {children}
        </AuthContext.Provider>
    );
};

AuthProvider.propTypes = {
    children: PropTypes.node.isRequired,
};

export default AuthContext;
