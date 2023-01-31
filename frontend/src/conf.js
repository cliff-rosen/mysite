const prod = {
  url: {
    //API_URL: "https://api-staging.trippersalmanac.com",
    API_URL: "https://",
  },
};

const dev = {
  url: {
    API_URL: "http://192.168.1.108:8000",
  },
};

export const config = process.env.NODE_ENV === "development" ? dev : prod;
