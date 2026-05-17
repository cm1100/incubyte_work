import { EmployeesTable } from "@/components/employees/employees-table";

export const metadata = {
  title: "Employees",
};

export default function EmployeesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Employees</h1>
        <p className="text-sm text-muted-foreground">
          Search, add, edit, and remove employees.
        </p>
      </div>
      <EmployeesTable />
    </div>
  );
}
