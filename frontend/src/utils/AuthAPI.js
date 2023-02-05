import { fetchGet, fetchPost } from "./APIUtils";

export const register = async (username, password) => {
  return fetchPost("users", { username, password });
};

/*

    API RESULT      JSON                STATUS  LOGIN RESULT
    success         {userID, token}     200     JSON
    invalid                             401     EXCEPTION INVALID_LOGIN                     
    fetch error                                 EXCEPTION res.error
    unknown error                               EXCEPTION UNKNOWN_LOGIN_ERROR
*/
export const login = async (username, password) => {
  return await fetchGet(`login?username=${username}&password=${password}`);
};
