import { LoginForm } from "@/components/LoginForm";
import { BrandLogo } from "@/components/ui/BrandLogo";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <section className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-6 text-center">
          <BrandLogo
            className="mx-auto h-auto max-h-44 w-full max-w-[22rem]"
            variant="full"
          />
          <h1 className="mt-4 text-2xl font-semibold text-slate-950">
            Agua Activa ERP
          </h1>
          <p className="mt-2 text-base font-medium text-water-700">
            Sistema de gestión operativa y control interno
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Accede para gestionar caja, ventas, rutas, producción, reportes y
            administración.
          </p>
        </div>
        <LoginForm />
      </section>
    </main>
  );
}
