"use client";

import { MessageSquare } from "lucide-react";

export function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="mb-8">
        <div className="w-24 h-24 rounded-full bg-white/10 flex items-center justify-center mb-6 mx-auto">
          <MessageSquare className="w-12 h-12 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-white mb-2">Sales Analytics Chat</h1>
        <p className="text-white/60 text-lg">
          Ask questions about your sales data in natural language
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full mt-8">
        <div className="p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-left">
          <h3 className="text-white font-medium mb-2">Example Questions</h3>
          <ul className="text-sm text-white/60 space-y-1">
            <li>• What are total sales by brand?</li>
            <li>• Compare sales this year vs last year</li>
            <li>• Show top 10 products by revenue</li>
          </ul>
        </div>
        <div className="p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-left">
          <h3 className="text-white font-medium mb-2">Capabilities</h3>
          <ul className="text-sm text-white/60 space-y-1">
            <li>• Natural language queries</li>
            <li>• SQL generation</li>
            <li>• Data visualization</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

