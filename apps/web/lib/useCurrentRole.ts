"use client";

import { useEffect, useState } from "react";

import { isAdminAuditor } from "@/lib/auth";


export function useIsAdminAuditor(): boolean {
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    setIsAdmin(isAdminAuditor());
  }, []);

  return isAdmin;
}
