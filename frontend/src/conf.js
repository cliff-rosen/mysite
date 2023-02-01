const prod = {
  url: {
    //API_URL: "https://api-staging.trippersalmanac.com",
    API_URL: "https://",
  },
};

const dev = {
  url: {
    API_URL: "http://127.0.0.1:8000/polls",
  },
};

export const config = process.env.NODE_ENV === "development" ? dev : prod;
