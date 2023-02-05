import { fetchPost } from "./APIUtils";

export const getAccess = async (password) => {
  var res;
  try {
    res = await fetchPost("access", { password });
    return res;
  } catch (e) {
    console.log("getAccess error: ", e.message);
    if (e.message === "UNAUTHORIZED") {
      console.log("AuthAPI.login - 401");
      throw new Error("INVALID_LOGIN");
    } else {
      throw new Error("UNKNOWN_LOGIN_ERROR");
    }
  }
};

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
  return await fetchPost("login", { username, password });
};
