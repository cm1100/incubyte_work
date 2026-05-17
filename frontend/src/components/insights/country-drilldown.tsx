"use client";

import { useMemo } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import {
  useInsightsByCountry,
  useInsightsByJobTitle,
  useInsightsPercentiles,
} from "@/lib/queries";

type Props = {
  country: string;
  onCountryChange: (next: string) => void;
};

export function CountryDrilldown({ country, onCountryChange }: Props) {
  const { data: countries } = useInsightsByCountry();
  const jobs = useInsightsByJobTitle(country);
  const percentiles = useInsightsPercentiles(country);

  const countryOptions = useMemo(
    () =>
      countries
        ? [...new Set(countries.map((c) => c.country))].sort()
        : [],
    [countries],
  );

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <CardTitle>Country drill-down</CardTitle>
        <Select
          value={country}
          onValueChange={(v) => v && onCountryChange(v)}
        >
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Country" />
          </SelectTrigger>
          <SelectContent>
            {countryOptions.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <h3 className="text-sm font-medium mb-2">Percentiles</h3>
          {percentiles.isLoading ? (
            <Skeleton className="h-16 w-full" />
          ) : percentiles.data && percentiles.data.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {percentiles.data.map((p) => (
                <div key={p.currency_code} className="contents">
                  {(["p25", "p50", "p75", "p90"] as const).map((k) => (
                    <PercentileTile
                      key={`${p.currency_code}-${k}`}
                      label={k.toUpperCase()}
                      value={p[k]}
                      currency={p.currency_code}
                    />
                  ))}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No data for {country}.</p>
          )}
        </div>

        <div>
          <h3 className="text-sm font-medium mb-2">By job title</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Job title</TableHead>
                <TableHead className="text-right">Count</TableHead>
                <TableHead className="hidden md:table-cell text-right">Min</TableHead>
                <TableHead className="text-right">Avg</TableHead>
                <TableHead className="hidden md:table-cell text-right">Max</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {jobs.isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 5 }).map((_, j) => (
                      <TableCell key={j}>
                        <Skeleton className="h-4 w-full" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : jobs.data && jobs.data.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-muted-foreground text-center py-6">
                    No active employees in {country}.
                  </TableCell>
                </TableRow>
              ) : (
                jobs.data?.map((j) => (
                  <TableRow key={`${j.job_title}-${j.currency_code}`}>
                    <TableCell>{j.job_title}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      {j.count.toLocaleString()}
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-right tabular-nums">
                      {formatMoney(j.min_salary, j.currency_code)}
                    </TableCell>
                    <TableCell className="text-right tabular-nums font-medium">
                      {formatMoney(j.avg_salary, j.currency_code)}
                    </TableCell>
                    <TableCell className="hidden md:table-cell text-right tabular-nums">
                      {formatMoney(j.max_salary, j.currency_code)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

function PercentileTile({
  label,
  value,
  currency,
}: {
  label: string;
  value: string;
  currency: string;
}) {
  return (
    <div className="rounded-md border p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-semibold tabular-nums">
        {formatMoney(value, currency)}
      </div>
    </div>
  );
}
