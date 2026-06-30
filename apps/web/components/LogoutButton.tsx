"use client";

import { useRouter } from "next/navigation";

import { removeToken } from "@/lib/auth";

export function LogoutButton() {
  const router = useRouter();

  function handleLogout() {
    removeToken();
    router.replace("/login");
  }

  return (
    <button
      className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:border-water-500 hover:text-water-700"
      type="button"
      onClick={handleLogout}
    >
      Cerrar sesión
    </button>
  );
}
