"use client";

import { Settings } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ChatHeader() {
  return (
    <div className="flex items-center justify-between p-4 border-b border-white/10 bg-[#171717]">
      <div className="flex items-center gap-2">
        <select className="bg-transparent text-white text-sm border-none outline-none cursor-pointer hover:text-white/80">
          <option>Quick Settings</option>
          <option>Settings</option>
          <option>Preferences</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-sm text-white/80">Sales Analytics AI</span>
        <Button
          variant="ghost"
          size="icon"
          className="text-white/60 hover:text-white hover:bg-white/10 h-8 w-8"
        >
          <Settings className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}

