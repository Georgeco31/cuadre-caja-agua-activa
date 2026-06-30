type LoadingStateProps = {
  label?: string;
};

export function LoadingState({ label = "Cargando..." }: LoadingStateProps) {
  return (
    <div className="flex min-h-64 items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-10">
      <p className="text-sm text-slate-600">{label}</p>
    </div>
  );
}
