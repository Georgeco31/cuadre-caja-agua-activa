"use client";

import { useEffect, useState } from "react";

import { getStoredRole } from "@/lib/auth";
import { canUseAdminActions } from "@/lib/frontendPermissions";
import type { UserRole } from "@/types/auth";

type CurrentRoleState = {
  isResolved: boolean;
  role: UserRole | null;
};

export function useCurrentRole(): CurrentRoleState {
  const [state, setState] = useState<CurrentRoleState>({
    isResolved: false,
    role: null,
  });

  useEffect(() => {
    setState({
      isResolved: true,
      role: getStoredRole(),
    });
  }, []);

  return state;
}

export function useIsAdminAuditor(): boolean {
  return canUseAdminActions(useCurrentRole().role);
}
