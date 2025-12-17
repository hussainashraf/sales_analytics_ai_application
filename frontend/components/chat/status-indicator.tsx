"use client";

import { Loader2, Code2, Database, MessageSquare, BarChart3 } from "lucide-react";

interface StatusIndicatorProps {
  step: "generating_sql" | "executing_sql" | "generating_answer" | "generating_chart";
  message: string;
}

export function StatusIndicator({ step, message }: StatusIndicatorProps) {
  const icons = {
    generating_sql: Code2,
    executing_sql: Database,
    generating_answer: MessageSquare,
    generating_chart: BarChart3,
  };

  const Icon = icons[step];

  return (
    <div className="flex gap-3 mb-4 px-4 animate-in fade-in slide-in-from-bottom-2">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
        <Loader2 className="w-4 h-4 text-white/60 animate-spin" />
      </div>
      <div className="bg-white/5 rounded-2xl px-4 py-3 border border-white/10 flex items-center gap-2">
        <Icon className="w-4 h-4 text-white/60" />
        <p className="text-sm text-white/60">{message}</p>
      </div>
    </div>
  );
}

