export type LoginCredentials = {
  username: string;
  password: string;
};

export type UserRole = "operator" | "admin_auditor";

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  role: UserRole;
};

export type CurrentUser = {
  id: number;
  username: string;
  role: UserRole;
  is_active: boolean;
};
