// Centralised display formatters. Money is formatted with the row's
// own currency so we never assume a default.

export function formatMoney(amount: string, currency: string): string {
  const n = Number(amount);
  if (!isFinite(n)) return `${amount} ${currency}`;
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(n);
  } catch {
    // Unknown ISO code → show raw value to avoid swallowing data.
    return `${amount} ${currency}`;
  }
}

const STATUS_LABELS: Record<string, string> = {
  active: "Active",
  on_leave: "On leave",
  terminated: "Terminated",
};

export function formatStatus(status: string): string {
  return STATUS_LABELS[status] ?? status;
}
