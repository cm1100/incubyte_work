"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ApiError } from "@/lib/api";
import type { EmployeeCreateInput } from "@/lib/types";

const schema = z.object({
  employee_id: z
    .string()
    .min(3, "Min 3 characters")
    .max(16, "Max 16 characters"),
  first_name: z.string().min(1, "Required").max(100),
  last_name: z.string().min(1, "Required").max(100),
  email: z.string().email("Not a valid email"),
  job_title: z.string().min(1, "Required").max(100),
  department: z.string().min(1, "Required").max(100),
  country: z
    .string()
    .regex(/^[A-Z]{2}$/, "Use 2-letter ISO code, e.g. IN, US, DE"),
  salary: z
    .string()
    .refine((v) => /^\d+(\.\d{1,2})?$/.test(v), "Number with up to 2 decimals")
    .refine((v) => Number(v) >= 0, "Cannot be negative"),
  currency_code: z
    .string()
    .regex(/^[A-Z]{3}$/, "Use 3-letter ISO code, e.g. INR, USD, EUR"),
  hire_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Use YYYY-MM-DD"),
  status: z.enum(["active", "on_leave", "terminated"]),
  employment_type: z.enum(["full_time", "part_time", "contract"]),
});

export type EmployeeFormValues = z.infer<typeof schema>;

type Props = {
  mode: "create" | "edit";
  defaultValues?: Partial<EmployeeFormValues>;
  submitLabel: string;
  isSubmitting: boolean;
  onSubmit: (values: EmployeeFormValues) => Promise<void>;
  error?: unknown;
};

export function EmployeeForm({
  mode,
  defaultValues,
  submitLabel,
  isSubmitting,
  onSubmit,
  error,
}: Props) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<EmployeeFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      employee_id: "",
      first_name: "",
      last_name: "",
      email: "",
      job_title: "",
      department: "",
      country: "",
      salary: "",
      currency_code: "",
      hire_date: "",
      status: "active",
      employment_type: "full_time",
      ...defaultValues,
    },
  });

  const status = watch("status");
  const employmentType = watch("employment_type");

  return (
    <form
      onSubmit={handleSubmit(async (v) => {
        await onSubmit(v);
      })}
      className="space-y-6"
    >
      {error ? <FormError error={error} /> : null}

      <Section title="Identification">
        <FieldGrid>
          <Field
            label="Employee ID"
            error={errors.employee_id?.message}
            disabled={mode === "edit"}
          >
            <Input
              placeholder="EMP-00042"
              {...register("employee_id")}
              disabled={mode === "edit"}
            />
          </Field>
          <Field label="Email" error={errors.email?.message}>
            <Input type="email" {...register("email")} />
          </Field>
        </FieldGrid>
      </Section>

      <Section title="Name">
        <FieldGrid>
          <Field label="First name" error={errors.first_name?.message}>
            <Input {...register("first_name")} />
          </Field>
          <Field label="Last name" error={errors.last_name?.message}>
            <Input {...register("last_name")} />
          </Field>
        </FieldGrid>
      </Section>

      <Section title="Role">
        <FieldGrid>
          <Field label="Job title" error={errors.job_title?.message}>
            <Input {...register("job_title")} />
          </Field>
          <Field label="Department" error={errors.department?.message}>
            <Input {...register("department")} />
          </Field>
        </FieldGrid>
      </Section>

      <Section title="Compensation">
        <FieldGrid cols={3}>
          <Field label="Country" error={errors.country?.message}>
            <Input placeholder="IN" maxLength={2} {...register("country")} />
          </Field>
          <Field label="Salary" error={errors.salary?.message}>
            <Input
              type="text"
              inputMode="decimal"
              placeholder="1500000.00"
              {...register("salary")}
            />
          </Field>
          <Field label="Currency" error={errors.currency_code?.message}>
            <Input placeholder="INR" maxLength={3} {...register("currency_code")} />
          </Field>
        </FieldGrid>
      </Section>

      <Section title="Employment">
        <FieldGrid cols={3}>
          <Field label="Hire date" error={errors.hire_date?.message}>
            <Input type="date" {...register("hire_date")} />
          </Field>
          <Field label="Status" error={errors.status?.message}>
            <Select
              value={status}
              onValueChange={(v) =>
                setValue("status", v as EmployeeFormValues["status"], { shouldValidate: true })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="on_leave">On leave</SelectItem>
                <SelectItem value="terminated">Terminated</SelectItem>
              </SelectContent>
            </Select>
          </Field>
          <Field label="Employment type" error={errors.employment_type?.message}>
            <Select
              value={employmentType}
              onValueChange={(v) =>
                setValue(
                  "employment_type",
                  v as EmployeeFormValues["employment_type"],
                  { shouldValidate: true },
                )
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="full_time">Full-time</SelectItem>
                <SelectItem value="part_time">Part-time</SelectItem>
                <SelectItem value="contract">Contract</SelectItem>
              </SelectContent>
            </Select>
          </Field>
        </FieldGrid>
      </Section>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving…" : submitLabel}
        </Button>
      </div>
    </form>
  );
}

// ----- presentational helpers -----

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h2 className="text-sm font-medium text-muted-foreground">{title}</h2>
      {children}
    </div>
  );
}

function FieldGrid({
  children,
  cols = 2,
}: {
  children: React.ReactNode;
  cols?: 2 | 3;
}) {
  return (
    <div
      className={`grid gap-4 ${cols === 3 ? "md:grid-cols-3" : "md:grid-cols-2"}`}
    >
      {children}
    </div>
  );
}

function Field({
  label,
  error,
  children,
  disabled,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
  disabled?: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <Label className={disabled ? "text-muted-foreground" : undefined}>
        {label}
      </Label>
      {children}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}

function FormError({ error }: { error: unknown }) {
  let title = "Could not save";
  let detail = "Unknown error";
  if (error instanceof ApiError) {
    if (error.status === 409) {
      title = "Already exists";
      detail =
        "An employee with this ID or email already exists. Pick a different one.";
    } else if (error.status === 422) {
      title = "Validation failed";
      detail = "The server rejected one or more fields. Check the highlighted ones above.";
    } else {
      detail = `HTTP ${error.status}`;
    }
  } else if (error instanceof Error) {
    detail = error.message;
  }
  return (
    <Alert variant="destructive">
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{detail}</AlertDescription>
    </Alert>
  );
}

// EmployeeCreateInput is structurally identical to EmployeeFormValues so the
// caller can pass straight through; keeping the type alias here documents that.
export type _Sanity = EmployeeCreateInput;
