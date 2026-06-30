"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { LogoutButton } from "@/components/LogoutButton";
import { getCurrentUser } from "@/lib/api";
import { getToken, removeToken } from "@/lib/auth";
import type { CurrentUser } from "@/types/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    getCurrentUser(token)
      .then((currentUser) => {
        setUser(currentUser);
      })
      .catch(() => {
        removeToken();
        router.replace("/login");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [router]);

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
        <p className="text-sm text-slate-600">Cargando dashboard...</p>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-water-700">Agua Activa</p>
            <h1 className="mt-1 text-2xl font-semibold text-slate-950">
              Dashboard
            </h1>
          </div>
          <LogoutButton />
        </header>

        <section className="grid flex-1 place-items-center py-10">
          <div className="w-full max-w-2xl rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-slate-950">
              Bienvenido, {user.username}
            </h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Sistema de cuadre diario de caja
            </p>
            <Link
              className="mt-6 inline-flex h-10 items-center rounded-md bg-water-700 px-4 text-sm font-semibold text-white transition hover:bg-water-500"
              href="/dashboard/cash-session"
            >
              Registrar cuadre diario
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
