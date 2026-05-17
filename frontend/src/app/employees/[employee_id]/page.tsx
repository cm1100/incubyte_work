"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import {
  EmployeeForm,
  type EmployeeFormValues,
} from "@/components/employees/employee-form";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";
import {
  useDeleteEmployee,
  useEmployee,
  useUpdateEmployee,
} from "@/lib/queries";

export default function EmployeeDetailPage() {
  const params = useParams<{ employee_id: string }>();
  const employeeId = params.employee_id;
  const router = useRouter();

  const { data: employee, isLoading, isError, error } = useEmployee(employeeId);
  const update = useUpdateEmployee(employeeId);
  const del = useDeleteEmployee();
  const [confirmOpen, setConfirmOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="max-w-3xl space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (isError) {
    const notFound = error instanceof ApiError && error.status === 404;
    return (
      <Alert variant="destructive" className="max-w-xl">
        <AlertTitle>{notFound ? "Not found" : "Failed to load"}</AlertTitle>
        <AlertDescription>
          {notFound
            ? `No employee with ID ${employeeId}.`
            : (error as Error)?.message}
        </AlertDescription>
      </Alert>
    );
  }

  if (!employee) return null;

  const defaults: EmployeeFormValues = {
    employee_id: employee.employee_id,
    first_name: employee.first_name,
    last_name: employee.last_name,
    email: employee.email,
    job_title: employee.job_title,
    department: employee.department,
    country: employee.country,
    salary: employee.salary,
    currency_code: employee.currency_code,
    hire_date: employee.hire_date,
    status: employee.status,
    employment_type: employee.employment_type,
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{employee.full_name}</h1>
          <p className="text-sm text-muted-foreground font-mono">
            {employee.employee_id}
          </p>
        </div>
        <Button variant="destructive" onClick={() => setConfirmOpen(true)}>
          Delete
        </Button>
        <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete {employee.full_name}?</DialogTitle>
              <DialogDescription>
                Permanently removes the record — there is no soft-delete.
                Insights will recalculate immediately.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setConfirmOpen(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                disabled={del.isPending}
                onClick={async () => {
                  await del.mutateAsync(employeeId);
                  toast.success(`Deleted ${employee.full_name}`);
                  router.push("/employees");
                }}
              >
                {del.isPending ? "Deleting…" : "Delete"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <EmployeeForm
        mode="edit"
        defaultValues={defaults}
        submitLabel="Save changes"
        isSubmitting={update.isPending}
        error={update.error}
        onSubmit={async (values) => {
          await update.mutateAsync(values);
          toast.success("Saved");
        }}
      />
    </div>
  );
}
