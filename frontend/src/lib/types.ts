// Types mirror backend Pydantic schemas. Salary/percentile fields are
// strings because the backend serialises Decimal as string to preserve
// money precision — never coerce to Number on the way through.

export type EmployeeStatus = "active" | "on_leave" | "terminated";
export type EmploymentType = "full_time" | "part_time" | "contract";

export type Employee = {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  job_title: string;
  department: string;
  country: string;
  salary: string;
  currency_code: string;
  hire_date: string;
  status: EmployeeStatus;
  employment_type: EmploymentType;
  created_at: string;
  updated_at: string;
};

export type EmployeeCreateInput = {
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  job_title: string;
  department: string;
  country: string;
  salary: string;
  currency_code: string;
  hire_date: string;
  status?: EmployeeStatus;
  employment_type?: EmploymentType;
};

export type EmployeeUpdateInput = Partial<Omit<EmployeeCreateInput, "employee_id">>;

export type EmployeePage = {
  items: Employee[];
  total: number;
  offset: number;
  limit: number;
};

export type CountrySalarySummary = {
  country: string;
  currency_code: string;
  count: number;
  min_salary: string;
  max_salary: string;
  avg_salary: string;
};

export type JobTitleSalarySummary = {
  job_title: string;
  currency_code: string;
  count: number;
  min_salary: string;
  max_salary: string;
  avg_salary: string;
};

export type CountryPercentiles = {
  country: string;
  currency_code: string;
  count: number;
  p25: string;
  p50: string;
  p75: string;
  p90: string;
};

export type HeadcountBucket = {
  name: string;
  count: number;
};

export type HeadcountBreakdown = {
  by_country: HeadcountBucket[];
  by_department: HeadcountBucket[];
  by_job_title: HeadcountBucket[];
};
