export function DataTable({ columns, rows, emptyText = "No records found." }) {
  return (
    <div className="theme-surface overflow-hidden rounded-[1.75rem]">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-emerald-100/70">
          <thead className="bg-emerald-50/55">
            <tr>
              {columns.map((column) => (
                <th key={column.key} className="px-4 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-emerald-50/80">
            {rows.length ? (
              rows.map((row, index) => (
                <tr key={row.id ?? row.patient_id ?? row.doctor_id ?? row.appointment_id ?? index} className="transition hover:bg-brand-50/35">
                  {columns.map((column) => (
                    <td key={column.key} className="px-4 py-4 text-sm text-slate-700">
                      {column.render ? column.render(row) : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-10 text-center text-sm text-slate-500" colSpan={columns.length}>
                  {emptyText}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
