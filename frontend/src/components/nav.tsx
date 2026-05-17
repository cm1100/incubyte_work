"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const TABS = [
  { href: "/employees", label: "Employees" },
  { href: "/insights", label: "Insights" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 max-w-7xl flex items-center h-14 gap-6">
        <Link href="/employees" className="font-semibold text-sm">
          Salary Management
        </Link>
        <nav className="flex items-center gap-1">
          {TABS.map((tab) => {
            const active = pathname.startsWith(tab.href);
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "px-3 py-1.5 text-sm rounded-md transition",
                  active
                    ? "bg-secondary text-secondary-foreground"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
