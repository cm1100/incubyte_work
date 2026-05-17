"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { HeadcountBucket } from "@/lib/types";
import { useInsightsHeadcount } from "@/lib/queries";

export function HeadcountCharts() {
  const { data, isLoading, isError } = useInsightsHeadcount();

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <ChartCard title="By country" data={data?.by_country} loading={isLoading} error={isError} />
      <ChartCard title="By department" data={data?.by_department} loading={isLoading} error={isError} />
      <ChartCard title="By job title" data={data?.by_job_title} loading={isLoading} error={isError} />
    </div>
  );
}

function ChartCard({
  title,
  data,
  loading,
  error,
}: {
  title: string;
  data?: HeadcountBucket[];
  loading: boolean;
  error: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-64 w-full" />
        ) : error ? (
          <p className="text-destructive text-sm">Failed to load.</p>
        ) : !data || data.length === 0 ? (
          <p className="text-muted-foreground text-sm">No data.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 4, right: 12, bottom: 4, left: 8 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={110}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip
                  cursor={{ fill: "rgba(0,0,0,0.05)" }}
                  contentStyle={{ fontSize: 12, borderRadius: 6 }}
                />
                <Bar dataKey="count" fill="var(--color-chart-2)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
