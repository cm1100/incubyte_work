"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatMoney } from "@/lib/format";
import { useInsightsByCountry } from "@/lib/queries";

export function CountrySummary() {
  const { data, isLoading, isError } = useInsightsByCountry();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Salary by country</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Country</TableHead>
              <TableHead>Currency</TableHead>
              <TableHead className="text-right">Count</TableHead>
              <TableHead className="text-right">Min</TableHead>
              <TableHead className="text-right">Avg</TableHead>
              <TableHead className="text-right">Max</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 6 }).map((_, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={6} className="text-destructive text-center py-8">
                  Failed to load country summaries.
                </TableCell>
              </TableRow>
            ) : data && data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-muted-foreground text-center py-8">
                  No active employees yet.
                </TableCell>
              </TableRow>
            ) : (
              data?.map((r) => (
                <TableRow key={`${r.country}-${r.currency_code}`}>
                  <TableCell className="font-medium">{r.country}</TableCell>
                  <TableCell className="text-muted-foreground">{r.currency_code}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {r.count.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatMoney(r.min_salary, r.currency_code)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums font-medium">
                    {formatMoney(r.avg_salary, r.currency_code)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatMoney(r.max_salary, r.currency_code)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
