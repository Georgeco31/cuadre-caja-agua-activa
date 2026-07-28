import {
  PRODUCT_CATEGORY_LABELS,
  PRODUCT_KIND_LABELS,
  PRODUCT_UNIT_LABELS,
  type Product,
} from "@/types/product";

type ProductListProps = {
  products: Product[];
  canManage?: boolean;
  hasActiveFilters?: boolean;
  changingProductId?: number | null;
  showSensitiveCosts?: boolean;
  onEdit: (product: Product) => void;
  onToggleActive: (product: Product) => void;
};

export function ProductList({
  products,
  canManage = true,
  hasActiveFilters = false,
  changingProductId = null,
  showSensitiveCosts = true,
  onEdit,
  onToggleActive,
}: ProductListProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Productos registrados
        </h2>
        <span className="text-sm text-slate-500">{products.length}</span>
      </div>

      {products.length === 0 ? (
        <p className="px-4 py-8 text-sm text-slate-600">
          {hasActiveFilters
            ? "No se encontraron productos con los filtros seleccionados."
            : "Todavía no hay productos registrados."}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1080px] border-collapse text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Producto</th>
                <th className="px-4 py-3 font-medium">Presentación</th>
                <th className="px-4 py-3 font-medium">Categoría</th>
                <th className="px-4 py-3 font-medium">Producción</th>
                <th className="px-4 py-3 font-medium">Precio base</th>
                {showSensitiveCosts ? (
                  <th className="px-4 py-3 font-medium">Costo estimado</th>
                ) : null}
                <th className="px-4 py-3 font-medium">Retornable</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                {canManage ? (
                  <th className="px-4 py-3 font-medium">Acciones</th>
                ) : null}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((product) => {
                const isChanging = changingProductId === product.id;

                return (
                  <tr key={product.id}>
                    <td className="px-4 py-3 align-top">
                      <p className="font-medium text-slate-950">{product.name}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {product.sku ?? "Sin SKU"}
                      </p>
                      {product.description ? (
                        <p className="mt-1 max-w-64 text-xs text-slate-500">
                          {product.description}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{product.presentation ?? "Sin presentación"}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {PRODUCT_UNIT_LABELS[product.unit]}
                      </p>
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      {PRODUCT_CATEGORY_LABELS[product.category]}
                    </td>
                    <td className="px-4 py-3 align-top text-slate-700">
                      <p>{PRODUCT_KIND_LABELS[product.product_kind]}</p>
                      {product.production_notes ? (
                        <p className="mt-1 max-w-56 text-xs text-slate-500">
                          {product.production_notes}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3 align-top font-medium text-slate-950">
                      {formatMoney(product.default_price)}
                    </td>
                    {showSensitiveCosts ? (
                      <td className="px-4 py-3 align-top text-slate-700">
                        {formatMoney(product.cost_estimate)}
                      </td>
                    ) : null}
                    <td className="px-4 py-3 align-top text-slate-700">
                      {product.is_returnable_container ? "Sí" : "No"}
                    </td>
                    {canManage ? (
                      <td className="px-4 py-3 align-top">
                      <span
                        className={
                          product.is_active
                            ? "inline-flex rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700"
                            : "inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600"
                        }
                      >
                        {product.is_active ? "Activo" : "Inactivo"}
                      </span>
                      </td>
                    ) : null}
                    <td className="px-4 py-3 align-top">
                      <div className="flex items-center gap-3">
                        <button
                          className="font-semibold text-water-700 hover:text-water-500 disabled:cursor-not-allowed disabled:text-slate-400"
                          type="button"
                          disabled={isChanging}
                          onClick={() => onEdit(product)}
                        >
                          Editar
                        </button>
                        <button
                          className={
                            product.is_active
                              ? "font-semibold text-red-700 hover:text-red-600 disabled:cursor-not-allowed disabled:text-slate-400"
                              : "font-semibold text-emerald-700 hover:text-emerald-600 disabled:cursor-not-allowed disabled:text-slate-400"
                          }
                          type="button"
                          disabled={isChanging}
                          onClick={() => onToggleActive(product)}
                        >
                          {isChanging
                            ? "Actualizando..."
                            : product.is_active
                              ? "Inactivar"
                              : "Reactivar"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function formatMoney(value: string): string {
  const [units, decimals = ""] = value.split(".");
  return `$${units}.${decimals.padEnd(2, "0").slice(0, 2)}`;
}
