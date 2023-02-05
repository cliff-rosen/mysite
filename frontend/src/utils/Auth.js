import { useState } from "react";
import { login as apiLogin, register as apiRegister } from "./AuthAPI";

const setStoredUser = (user) => {
  localStorage.setItem("user", JSON.stringify(user));
};

const p_register = async (username, password) => {
  return apiRegister(username, password)
    .then((user) => {
      console.log("Auth.register success", user);
      setStoredUser(user);
      return Promise.resolve("success");
    })
    .catch((e) => {
      console.log("Auth.register error - ", e.message);
      return Promise.reject(e);
    });
};

const p_login = async (username, password) => {
  return apiLogin(username, password)
    .then((u) => {
      console.log("Auth.login success", u);
      const user = {
        userID: u.user_id,
        domainID: u.domain_id,
        userName: u.user_name,
      };
      setStoredUser(user);
      return Promise.resolve("success");
    })
    .catch((e) => {
      console.log("Auth.login error - ", e);
      return Promise.reject(e);
    });
};

const p_logout = () => {
  setStoredUser({ userID: 0 });
};

export const getUser = () => {
  let user;
  try {
    user = JSON.parse(localStorage.getItem("user"));
    if (user == null) {
      user = { userID: 0 };
      setStoredUser(user);
    }
  } catch {
    user = { userID: 0 };
    setStoredUser(user);
  }

  return user;
};

export const getUserFromStorage = () => {
  var userFromStorage;

  try {
    userFromStorage = JSON.parse(localStorage.getItem("user"));
  } catch {
    userFromStorage = { userID: 0, token: "" };
  }
  return userFromStorage;
};

export const getUserToken = () => {
  var user;

  try {
    user = JSON.parse(localStorage.getItem("user"));
  } catch {
    user = { userID: -1, token: "" };
  }
  if (user.userID > 0) {
    return "Bearer " + user.token;
  }
  return "";
};

const makeLoginActionObject = () => {
  return {
    show: false,
    message: "",
    mode: null,
    fn: null,
    params: null,
    homeOnAbort: false,
  };
};

export const useSessionManager = () => {
  const [user, setUser] = useState(getUser());
  const [lao, setLao] = useState(makeLoginActionObject());
  const [showSessionMessage, setShowSessionMessage] = useState(false);
  const [sessionMessage, setSessionMessage] = useState("");

  const showLogin = (message) => {
    setLao({ ...lao, show: true, message });
  };

  const hideLogin = () => {
    setLao(makeLoginActionObject());
  };

  const showLoginThen = (fn, params) => {
    const message = "Please login to use this function.";
    setLao((curLao) => {
      return { ...curLao, show: true, fn, params, message };
    });
  };

  const hideLoginThen = (u) => {
    if (lao.fn) {
      console.log("hideLoginThen: ", u);
      lao.fn.apply(null, lao.params);
    }
    setLao(makeLoginActionObject());
  };

  // add to component requiring logged in user
  // must be in useEffect/event handler to avoid running while parent renders
  const requireUser = () => {
    if (user.userID === 0 && lao.show === false) {
      showLogin("Please login to use this feature.");
      setLao((curLao) => {
        return { ...curLao, homeOnAbort: true };
      });
    }
  };

  const register = async (username, password) => {
    await p_register(username, password);
    const u = getUser();
    setUser(u);
    return u;
  };

  const login = async (username, password) => {
    console.log("SessionManager login");
    await p_login(username, password);
    const u = getUser();
    setUser(u);
    return u;
  };

  const logout = () => {
    p_logout();
    setUser(getUser());
  };

  const setSessionMessageWrapper = (message) => {
    console.log("show message", message);
    setSessionMessage(message);
    setShowSessionMessage(true);
  };

  return {
    user,
    lao,
    getUserFromStorage,
    showLogin,
    showLoginThen,
    hideLogin,
    hideLoginThen,
    register,
    login,
    logout,
    requireUser,
    sessionMessage,
    setSessionMessageWrapper,
    showSessionMessage,
    setShowSessionMessage,
  };
};
