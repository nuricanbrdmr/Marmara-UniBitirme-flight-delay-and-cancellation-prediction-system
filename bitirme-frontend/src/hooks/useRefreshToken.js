import axios from '../api/axios';
import useAuth from './useAuth';
import Cookies from "js-cookie";

const useRefreshToken = () => {
    const { setAuth } = useAuth();
    const refreshToken = Cookies.get("refreshToken")
    const refresh = async () => {
        try {
            const response = await axios.post('/auth/refreshToken', {
                token: refreshToken
            }, {
                withCredentials: true
            });
            setAuth(prev => ({
                ...prev,
                accessToken: response.data.accessToken
            }));
            return response.data.accessToken;
        } catch (error) {
            console.error('Refresh token error:', error);
            throw error;
        }
    };

    return refresh;
};

export default useRefreshToken;