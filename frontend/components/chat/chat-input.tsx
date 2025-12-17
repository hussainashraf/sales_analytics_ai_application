"use client";

import { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2, Plus, HelpCircle } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, isLoading, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() && !isLoading && !disabled) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative p-4 border-t border-white/10 bg-[#171717]">
      <div className="flex items-center gap-2 max-w-3xl mx-auto">
        <Button
          variant="ghost"
          size="icon"
          className="text-white/60 hover:text-white hover:bg-white/10 h-9 w-9 shrink-0"
        >
          <Plus className="w-4 h-4" />
        </Button>
        
        <div className="flex-1 relative">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Send a message..."
            disabled={isLoading || disabled}
            className="bg-[#262626] border-white/10 text-white placeholder:text-white/40 pr-12 h-11 focus-visible:ring-1 focus-visible:ring-white/20"
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || disabled}
            size="icon"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9 bg-transparent hover:bg-white/10 text-white/60 hover:text-white"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="text-white/60 hover:text-white hover:bg-white/10 h-9 w-9 shrink-0"
        >
          <HelpCircle className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}

