"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatMoney, formatStatus } from "@/lib/format";
import { useEmployees } from "@/lib/queries";

const PAGE_SIZE = 25;

function useDebounced<T>(value: T, delay = 250): T {
  const [out, setOut] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setOut(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return out;
}

export function EmployeesTable() {
  const [searchInput, setSearchInput] = useState("");
  const [offset, setOffset] = useState(0);
  const search = useDebounced(searchInput);

  // Reset to page 1 whenever the search changes — paginating on the old
  // filter is a footgun.
  useEffect(() => {
    setOffset(0);
  }, [search]);

  const { data, isLoading, isError, error } = useEmployees({
    offset,
    limit: PAGE_SIZE,
    search: search || undefined,
  });

  const showingTo = useMemo(() => {
    if (!data) return 0;
    return Math.min(offset + data.items.length, data.total);
  }, [data, offset]);

  return (
    <div className="space-y-4">
      {/* flex-wrap so on narrow screens the Add button drops below the search */}
      <div className="flex flex-wrap items-center gap-3">
        <Input
          placeholder="Search by name, email, or employee ID…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="flex-1 min-w-[200px] max-w-sm"
        />
        <Link href="/employees/new" className="ml-auto">
          <Button>Add employee</Button>
        </Link>
      </div>

      {/* Horizontal scroll as a fallback; the column visibility classes below
          mean users mostly won't need it on common phone widths. */}
      <div className="rounded-md border overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="hidden sm:table-cell w-[120px]">ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead className="hidden md:table-cell">Job title</TableHead>
              <TableHead className="hidden lg:table-cell">Department</TableHead>
              <TableHead className="hidden md:table-cell">Country</TableHead>
              <TableHead className="text-right">Salary</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && !data ? (
              Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell className="hidden sm:table-cell"><Skeleton className="h-4 w-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-full" /></TableCell>
                  <TableCell className="hidden md:table-cell"><Skeleton className="h-4 w-full" /></TableCell>
                  <TableCell className="hidden lg:table-cell"><Skeleton className="h-4 w-full" /></TableCell>
                  <TableCell className="hidden md:table-cell"><Skeleton className="h-4 w-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-full" /></TableCell>
                </TableRow>
              ))
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={7} className="text-destructive text-center py-8">
                  {(error as Error)?.message ?? "Failed to load employees."}
                </TableCell>
              </TableRow>
            ) : data && data.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-muted-foreground text-center py-8">
                  No employees match this search.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((e) => (
                <TableRow key={e.id}>
                  <TableCell className="font-mono text-xs hidden sm:table-cell">
                    <Link
                      href={`/employees/${e.employee_id}`}
                      className="hover:underline"
                    >
                      {e.employee_id}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Link href={`/employees/${e.employee_id}`} className="hover:underline">
                      {e.full_name}
                    </Link>
                    {/* Surface hidden context inline on mobile so the row
                        stays informative — employee_id, email, job/country
                        all collapse into the Name cell below sm. */}
                    <div className="text-[10px] text-muted-foreground font-mono sm:hidden">
                      {e.employee_id}
                    </div>
                    <div className="text-xs text-muted-foreground truncate max-w-[200px]">
                      {e.email}
                    </div>
                    <div className="text-xs text-muted-foreground md:hidden mt-0.5">
                      {e.job_title} · {e.country}
                    </div>
                  </TableCell>
                  <TableCell className="hidden md:table-cell">{e.job_title}</TableCell>
                  <TableCell className="hidden lg:table-cell">{e.department}</TableCell>
                  <TableCell className="hidden md:table-cell">{e.country}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatMoney(e.salary, e.currency_code)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={e.status === "active" ? "default" : "secondary"}>
                      {formatStatus(e.status)}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div>
          {data
            ? `Showing ${data.total === 0 ? 0 : offset + 1}–${showingTo} of ${data.total.toLocaleString()}`
            : "—"}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={offset === 0 || isLoading}
            onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!data || offset + PAGE_SIZE >= data.total || isLoading}
            onClick={() => setOffset((o) => o + PAGE_SIZE)}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
