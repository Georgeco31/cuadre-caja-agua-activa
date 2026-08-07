"use client";

import { useParams } from "next/navigation";

import { SimpleRouteSheetWorkspace } from "@/components/SimpleRouteSheetWorkspace";

export default function SimpleRouteDetailPage() {
  const params = useParams<{ id: string }>();
  const sheetId = Number(params.id);

  if (!Number.isInteger(sheetId) || sheetId <= 0) {
    return <main className="min-h-screen bg-slate-50 p-6 text-sm text-red-700">La hoja de ruta solicitada no es válida.</main>;
  }

  return <SimpleRouteSheetWorkspace sheetId={sheetId} />;
}
