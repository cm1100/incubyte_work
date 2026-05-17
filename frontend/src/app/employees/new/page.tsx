"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";

import {
  EmployeeForm,
  type EmployeeFormValues,
} from "@/components/employees/employee-form";
import { useCreateEmployee } from "@/lib/queries";

export default function NewEmployeePage() {
  const router = useRouter();
  const mutation = useCreateEmployee();

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold">Add employee</h1>
        <p className="text-sm text-muted-foreground">
          New record. Employee ID and email must be unique.
        </p>
      </div>
      <EmployeeForm
        mode="create"
        submitLabel="Create employee"
        isSubmitting={mutation.isPending}
        error={mutation.error}
        onSubmit={async (values: EmployeeFormValues) => {
          const created = await mutation.mutateAsync(values);
          toast.success(`Created ${created.full_name}`);
          router.push(`/employees/${created.employee_id}`);
        }}
      />
    </div>
  );
}
