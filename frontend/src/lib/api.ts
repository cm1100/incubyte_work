import type {
  CountryPercentiles,
  CountrySalarySummary,
  Employee,
  EmployeeCreateInput,
  EmployeePage,
  EmployeeUpdateInput,
  HeadcountBreakdown,
  JobTitleSalarySummary,
} from "@/lib/types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8765";

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
  ) {
    super(`HTTP ${status}`);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

function qs(params: Record<string, string | number | undefined>): string {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== "",
  );
  if (entries.length === 0) return "";
  return "?" + entries.map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`).join("&");
}

export const api = {
  // ----- employees -----
  listEmployees: (params: {
    offset?: number;
    limit?: number;
    search?: string;
  }) => request<EmployeePage>(`/employees${qs(params)}`),

  getEmployee: (employeeId: string) =>
    request<Employee>(`/employees/${employeeId}`),

  createEmployee: (data: EmployeeCreateInput) =>
    request<Employee>("/employees", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateEmployee: (employeeId: string, data: EmployeeUpdateInput) =>
    request<Employee>(`/employees/${employeeId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteEmployee: (employeeId: string) =>
    request<void>(`/employees/${employeeId}`, { method: "DELETE" }),

  // ----- insights -----
  insightsByCountry: () =>
    request<CountrySalarySummary[]>("/insights/by-country"),

  insightsByJobTitle: (country: string) =>
    request<JobTitleSalarySummary[]>(
      `/insights/by-country/${country}/by-job-title`,
    ),

  insightsPercentiles: (country: string) =>
    request<CountryPercentiles[]>(
      `/insights/by-country/${country}/percentiles`,
    ),

  insightsHeadcount: () => request<HeadcountBreakdown>("/insights/headcount"),
};
