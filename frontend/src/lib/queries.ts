import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { api } from "@/lib/api";
import type {
  EmployeeCreateInput,
  EmployeeUpdateInput,
} from "@/lib/types";

// Query keys live in one place so cache invalidation is consistent.
export const keys = {
  employees: (params: { offset?: number; limit?: number; search?: string }) =>
    ["employees", params] as const,
  employee: (employeeId: string) => ["employee", employeeId] as const,
  insightsByCountry: ["insights", "by-country"] as const,
  insightsByJobTitle: (country: string) =>
    ["insights", "by-job-title", country] as const,
  insightsPercentiles: (country: string) =>
    ["insights", "percentiles", country] as const,
  insightsHeadcount: ["insights", "headcount"] as const,
};

// ----- employees -----

export function useEmployees(params: {
  offset?: number;
  limit?: number;
  search?: string;
}) {
  return useQuery({
    queryKey: keys.employees(params),
    queryFn: () => api.listEmployees(params),
    placeholderData: (prev) => prev,
  });
}

export function useEmployee(employeeId: string) {
  return useQuery({
    queryKey: keys.employee(employeeId),
    queryFn: () => api.getEmployee(employeeId),
    enabled: Boolean(employeeId),
  });
}

export function useCreateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: EmployeeCreateInput) => api.createEmployee(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["employees"] });
      qc.invalidateQueries({ queryKey: ["insights"] });
    },
  });
}

export function useUpdateEmployee(employeeId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: EmployeeUpdateInput) =>
      api.updateEmployee(employeeId, data),
    onSuccess: (updated) => {
      qc.setQueryData(keys.employee(employeeId), updated);
      qc.invalidateQueries({ queryKey: ["employees"] });
      qc.invalidateQueries({ queryKey: ["insights"] });
    },
  });
}

export function useDeleteEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (employeeId: string) => api.deleteEmployee(employeeId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["employees"] });
      qc.invalidateQueries({ queryKey: ["insights"] });
    },
  });
}

// ----- insights -----

export function useInsightsByCountry() {
  return useQuery({
    queryKey: keys.insightsByCountry,
    queryFn: () => api.insightsByCountry(),
  });
}

export function useInsightsByJobTitle(country: string) {
  return useQuery({
    queryKey: keys.insightsByJobTitle(country),
    queryFn: () => api.insightsByJobTitle(country),
    enabled: Boolean(country),
  });
}

export function useInsightsPercentiles(country: string) {
  return useQuery({
    queryKey: keys.insightsPercentiles(country),
    queryFn: () => api.insightsPercentiles(country),
    enabled: Boolean(country),
  });
}

export function useInsightsHeadcount() {
  return useQuery({
    queryKey: keys.insightsHeadcount,
    queryFn: () => api.insightsHeadcount(),
  });
}
