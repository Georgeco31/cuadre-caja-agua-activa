import { LoginForm } from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <section className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6">
          <p className="text-sm font-medium text-water-700">Agua Activa</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-950">
            Cuadre de Caja Agua Activa
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Inicia sesión para registrar el cuadre diario
          </p>
        </div>
        <LoginForm />
      </section>
    </main>
  );
}
