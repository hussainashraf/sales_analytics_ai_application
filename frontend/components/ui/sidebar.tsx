"use client";

import { useState } from "react";
import { Button } from "./button";
import { Input } from "./input";
import {
  MessageSquare,
  Settings,
  FileEdit,
  FileText,
  BookOpen,
  Calendar,
  User,
  Plus,
  FolderUp,
  Search,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onNewChat: () => void;
}

export function Sidebar({ onNewChat }: SidebarProps) {
  const [selectedWorkspace, setSelectedWorkspace] = useState("Sales Analytics");

  return (
    <div className="flex h-screen bg-[#171717] text-white border-r border-white/10">
      {/* Vertical Icon Bar */}
      <div className="flex flex-col items-center gap-4 p-3 border-r border-white/10">
        <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <MessageSquare className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <Settings className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <FileEdit className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <FileText className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <BookOpen className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <Calendar className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-lg hover:bg-white/10 transition-colors mt-auto">
          <User className="w-5 h-5" />
        </button>
      </div>

      {/* Main Sidebar Content */}
      <div className="flex flex-col w-64 p-4 gap-4">
        {/* Workspace Selector */}
        <div className="relative">
          <select
            value={selectedWorkspace}
            onChange={(e) => setSelectedWorkspace(e.target.value)}
            className="w-full bg-[#262626] border border-white/10 rounded-lg px-3 py-2 text-sm text-white appearance-none cursor-pointer hover:bg-[#2a2a2a] transition-colors pr-8"
          >
            <option value="Sales Analytics">Sales Analytics</option>
            <option value="Workspace 1">Workspace 1</option>
            <option value="Workspace 2">Workspace 2</option>
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg
              className="w-4 h-4 text-white/60"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>

        {/* New Chat Button */}
        <div className="flex gap-2">
          <Button
            onClick={onNewChat}
            className="flex-1 bg-white text-black hover:bg-white/90 h-9 font-medium"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Button>
          <Button
            variant="outline"
            className="border-white/20 text-white hover:bg-white/10 h-9"
            size="icon"
          >
            <FolderUp className="w-4 h-4" />
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <Input
            placeholder="Search chats..."
            className="bg-[#262626] border-white/10 text-white placeholder:text-white/40 pl-9 h-9"
          />
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          <p className="text-sm text-white/40 px-2 py-4">No chats.</p>
        </div>
      </div>
    </div>
  );
}

