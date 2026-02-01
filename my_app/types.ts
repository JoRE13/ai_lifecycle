export type RegisterPost = {
  email: string;
  password: string;
};

export type LogIn = {
  access_token: string;
  token_type: "bearer";
};

export type LogInFail = {
  detail: [
    {
      loc: [string, number];
      msg: string;
      type: string;
    },
  ];
};
