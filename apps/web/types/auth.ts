export type LoginCredentials = {
  username: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};

export type CurrentUser = {
  id: number;
  username: string;
  is_active: boolean;
  created_at: string;
};
