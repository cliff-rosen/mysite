import { config } from "../conf";
//import { getUserToken } from "./Auth";

export const BASE_API_URL = config.url.API_URL;

function getHeaders(token) {
  const headers = {
    "X-CSRFToken": token,
    "Content-Type": "application/json",
  };

  /*
  const authProperty = getUserToken();

  if (authProperty !== "") {
    headers["Authorization"] = authProperty;
  }
  */
  return headers;
}

/*
    doFetch(method, endpoint, [body])
    returns json from API endpoint
    throws error if:
        fetch status !== 200
        fetch doesn't return parsable json
        parsed json includes "error" property
*/
async function doFetch(method, endpoint, body, token) {
  if (method !== "GET" && method !== "POST" && method !== "PUT") {
    console.log("doFetch called with invalid method:", method);
    throw new Error("doFetch called with invalid method:" + method);
  }

  const headers = getHeaders(token);
  const options = {
    method,
    headers,
  };
  if (body) {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${BASE_API_URL}/${endpoint}`, options);
  const data = await res.json();

  if (res.status === 401) {
    throw new Error("UNAUTHORIZED");
  } else if (res.status !== 200 || data.error) {
    throw new Error(
      `doFetch error. [status=${res.status}, error=${data?.error}]`
    );
  }

  return data;
}

export async function fetchGet(endpoint) {
  console.log("fetchGet", endpoint);
  return doFetch("GET", endpoint);
}

export async function fetchPost(endpoint, body) {
  console.log("fetchPost", endpoint);
  const token = await fetchGet("polls/get_token");
  console.log("token", token);
  return doFetch("POST", endpoint, body, token.token);
}

export async function fetchPut(endpoint, body) {
  console.log("fetchPut", endpoint);
  return doFetch("PUT", endpoint, body);
}
