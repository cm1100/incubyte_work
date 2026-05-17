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
      <div className="flex items-center gap-3">
        <Input
          placeholder="Search by name, email, or employee ID…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="max-w-sm"
        />
        <div className="ml-auto">
          <Link href="/employees/new">
            <Button>Add employee</Button>
          </Link>
        </div>
      </div>

      <div className="rounded-md border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[120px]">ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Job title</TableHead>
              <TableHead>Department</TableHead>
              <TableHead>Country</TableHead>
              <TableHead className="text-right">Salary</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && !data ? (
              Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
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
                  <TableCell className="font-mono text-xs">
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
                    <div className="text-xs text-muted-foreground">{e.email}</div>
                  </TableCell>
                  <TableCell>{e.job_title}</TableCell>
                  <TableCell>{e.department}</TableCell>
                  <TableCell>{e.country}</TableCell>
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
