import Link from "next/link";
import type { ReactNode } from "react";

type DashboardShellProps = {
  activeHref: string;
  alertsHref?: string;
  children: ReactNode;
  dateLabel: string;
  moduleHref?: string;
  roleLabel?: string;
  userName?: string;
};

const navigation = [
  { href: "/dashboard", label: "Inicio", icon: "⌂" },
  { href: "/dashboard/cash-session", label: "Caja", icon: "$" },
  { href: "/dashboard/delivery-routes", label: "Rutas", icon: "↗" },
  { href: "/dashboard/reports", label: "Reportes", icon: "▤" },
] as const;

export function DashboardShell({
  activeHref,
  alertsHref = "/dashboard#alertas",
  children,
  dateLabel,
  moduleHref = "/dashboard#modulos",
  roleLabel,
  userName = "Agua Activa",
}: DashboardShellProps) {
  return (
    <div className="min-h-screen overflow-x-clip bg-slate-50">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col bg-water-900 px-4 py-5 text-white shadow-xl lg:flex">
        <Link
          className="flex items-center gap-3 rounded-2xl px-2 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/80"
          href="/dashboard"
        >
          <span
            aria-hidden="true"
            className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-sm font-black tracking-tight text-water-800 shadow-sm"
          >
            AA
          </span>
          <span>
            <span className="block text-base font-semibold">Agua Activa</span>
            <span className="mt-0.5 block text-xs text-water-100">
              Gestión ERP
            </span>
          </span>
        </Link>

        <p className="mb-2 mt-9 px-3 text-[11px] font-bold uppercase tracking-[0.18em] text-water-200">
          Principal
        </p>
        <nav aria-label="Navegación principal" className="space-y-1">
          {navigation.map((item) => {
            const isActive = activeHref === item.href;
            return (
              <Link
                aria-current={isActive ? "page" : undefined}
                className={
                  isActive
                    ? "flex min-h-11 items-center gap-3 rounded-xl bg-white px-3 py-2.5 text-sm font-semibold text-water-900 shadow-sm"
                    : "flex min-h-11 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-water-50 transition hover:bg-white/10 hover:text-white"
                }
                href={item.href}
                key={item.href}
              >
                <span
                  aria-hidden="true"
                  className={
                    isActive
                      ? "inline-flex h-7 w-7 items-center justify-center rounded-lg bg-water-50 text-xs font-bold text-water-700"
                      : "inline-flex h-7 w-7 items-center justify-center rounded-lg bg-white/10 text-xs font-bold"
                  }
                >
                  {item.icon}
                </span>
                {item.label}
              </Link>
            );
          })}
          <Link
            className="flex min-h-11 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-water-50 transition hover:bg-white/10 hover:text-white"
            href={moduleHref}
          >
            <span
              aria-hidden="true"
              className="inline-flex h-7 w-7 items-center justify-center rounded-lg bg-white/10 text-xs font-bold"
            >
              •••
            </span>
            Más módulos
          </Link>
        </nav>

        <div className="mt-auto rounded-2xl border border-white/10 bg-white/10 p-4">
          <p className="text-xs font-medium text-water-100">Sesión activa</p>
          <p className="mt-1 truncate text-sm font-semibold text-white">
            {userName}
          </p>
          {roleLabel ? (
            <p className="mt-1 text-xs text-water-100">{roleLabel}</p>
          ) : null}
        </div>
      </aside>

      <div className="min-h-screen lg:pl-64">
        <header className="sticky top-0 z-20 border-b border-slate-200/90 bg-white/95 backdrop-blur">
          <div className="flex h-16 items-center gap-3 px-4 sm:px-6 xl:px-8">
            <Link
              aria-label="Ir al inicio"
              className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-water-800 text-xs font-black text-white lg:hidden"
              href="/dashboard"
            >
              AA
            </Link>
            <Link
              className="hidden h-10 min-w-0 max-w-md flex-1 items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-500 transition hover:border-water-200 hover:bg-white hover:text-water-700 sm:flex"
              href={moduleHref}
            >
              <span aria-hidden="true" className="text-base">
                ⌕
              </span>
              <span className="truncate">Buscar un módulo</span>
            </Link>
            <div className="ml-auto flex items-center gap-2 sm:gap-3">
              <time className="hidden text-sm font-medium text-slate-600 md:block">
                {dateLabel}
              </time>
              <Link
                aria-label="Ver avisos"
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 transition hover:border-water-200 hover:text-water-700"
                href={alertsHref}
              >
                <span aria-hidden="true">!</span>
              </Link>
              <div className="hidden items-center gap-2 border-l border-slate-200 pl-3 sm:flex">
                <span
                  aria-hidden="true"
                  className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-water-100 text-xs font-bold uppercase text-water-800"
                >
                  {userName.slice(0, 2)}
                </span>
                <span className="hidden min-w-0 xl:block">
                  <span className="block max-w-40 truncate text-sm font-semibold text-slate-800">
                    {userName}
                  </span>
                  {roleLabel ? (
                    <span className="block text-xs text-slate-500">
                      {roleLabel}
                    </span>
                  ) : null}
                </span>
              </div>
            </div>
          </div>
        </header>

        <main className="min-w-0 pb-[calc(7rem+env(safe-area-inset-bottom))] lg:pb-10">
          {children}
        </main>
      </div>

      <nav
        aria-label="Navegación móvil"
        className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t border-slate-200 bg-white/95 px-1 pb-[max(0.35rem,env(safe-area-inset-bottom))] pt-1.5 shadow-[0_-10px_30px_rgba(15,23,42,0.08)] backdrop-blur lg:hidden"
      >
        {navigation.map((item) => {
          const isActive = activeHref === item.href;
          return (
            <Link
              aria-current={isActive ? "page" : undefined}
              className={
                isActive
                  ? "flex min-h-14 flex-col items-center justify-center gap-1 rounded-xl text-[11px] font-semibold text-water-700"
                  : "flex min-h-14 flex-col items-center justify-center gap-1 rounded-xl text-[11px] font-medium text-slate-500"
              }
              href={item.href}
              key={item.href}
            >
              <span aria-hidden="true" className="text-base font-bold">
                {item.icon}
              </span>
              {item.label}
            </Link>
          );
        })}
        <Link
          className="flex min-h-14 flex-col items-center justify-center gap-1 rounded-xl text-[11px] font-medium text-slate-500"
          href={moduleHref}
        >
          <span aria-hidden="true" className="text-base font-bold">
            •••
          </span>
          Más
        </Link>
      </nav>
    </div>
  );
}
