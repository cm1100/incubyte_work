"use client";

import { useEffect, useState } from "react";

import { CountryDrilldown } from "@/components/insights/country-drilldown";
import { CountrySummary } from "@/components/insights/country-summary";
import { HeadcountCharts } from "@/components/insights/headcount-charts";
import { useInsightsByCountry } from "@/lib/queries";

export default function InsightsPage() {
  const { data: countries } = useInsightsByCountry();
  const [selected, setSelected] = useState<string>("");

  // Default the drill-down to the first country that has data, once it loads.
  useEffect(() => {
    if (!selected && countries && countries.length > 0) {
      setSelected(countries[0].country);
    }
  }, [countries, selected]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Insights</h1>
        <p className="text-sm text-muted-foreground">
          Salary distributions and headcount across the org. Active employees
          only — terminated rows are excluded from every aggregate.
        </p>
      </div>

      <CountrySummary />

      {selected ? (
        <CountryDrilldown country={selected} onCountryChange={setSelected} />
      ) : null}

      <HeadcountCharts />
    </div>
  );
}
