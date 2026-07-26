import type { UserRole } from "@/types/auth";

export type User = {
  id: number;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type UserCreatePayload = {
  username: string;
  password: string;
  role: UserRole;
  is_active: boolean;
};

export type UserUpdatePayload = {
  username?: string;
  password?: string;
  role?: UserRole;
  is_active?: boolean;
};
