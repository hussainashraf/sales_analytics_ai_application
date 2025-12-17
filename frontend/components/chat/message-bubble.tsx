"use client";

import { ChatMessage } from "@/types/chat";
import { cn } from "@/lib/utils";
import { Bot, User, Code2, Database } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-4 mb-6 px-4 animate-in fade-in slide-in-from-bottom-2",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div
        className={cn(
          "flex flex-col gap-2 max-w-[80%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        {/* 1. SQL Command - Show first */}
        {message.sql && (
          <div className="w-full rounded-lg bg-[#1a1a1a] border border-white/10 p-3">
            <div className="flex items-center gap-2 mb-2">
              <Code2 className="w-4 h-4 text-white/60" />
              <span className="text-xs font-medium text-white/60">
                Generated SQL
              </span>
            </div>
            <pre className="text-xs font-mono text-white/90 overflow-x-auto">
              <code>{message.sql}</code>
            </pre>
          </div>
        )}

        {/* 2. Results - Show second */}
        {message.data && message.data.length > 0 && (
          <div className="w-full rounded-lg bg-[#1a1a1a] border border-white/10 p-3">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-4 h-4 text-white/60" />
              <span className="text-xs font-medium text-white/60">
                Results ({message.data.length} rows)
              </span>
            </div>
            <div className="text-xs text-white/70 max-h-40 overflow-y-auto">
              <pre className="font-mono">
                {JSON.stringify(message.data.slice(0, 5), null, 2)}
                {message.data.length > 5 && (
                  <span className="text-white/50">
                    {"\n  ... and "}
                    {message.data.length - 5} more rows
                  </span>
                )}
              </pre>
            </div>
          </div>
        )}

        {/* 2.5. Chart Image - Show after results, before answer */}
        {message.chartImage && (
          <div className="w-full rounded-lg bg-[#1a1a1a] border border-white/10 p-3">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span className="text-xs font-medium text-white/60">
                Generated Chart
              </span>
            </div>
            <img 
              src={`data:image/png;base64,${message.chartImage}`}
              alt="Generated chart"
              className="w-full rounded-lg"
            />
          </div>
        )}

        {/* 3. Final Answer - Show last */}
        {message.content && (
          <div
            className={cn(
              "rounded-2xl px-4 py-3 prose prose-invert prose-sm max-w-none",
              isUser
                ? "bg-white text-black prose-p:text-black prose-strong:text-black"
                : "bg-white/5 text-white border border-white/10 prose-p:text-white prose-strong:text-white prose-headings:text-white prose-code:text-white prose-pre:bg-[#1a1a1a] prose-pre:border prose-pre:border-white/10"
            )}
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                em: ({ children }) => <em className="italic">{children}</em>,
                code: ({ children, className }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="bg-white/10 px-1.5 py-0.5 rounded text-xs font-mono">
                      {children}
                    </code>
                  ) : (
                    <code className={className}>{children}</code>
                  );
                },
                pre: ({ children }) => (
                  <pre className="bg-[#1a1a1a] border border-white/10 rounded-lg p-3 overflow-x-auto my-2">
                    {children}
                  </pre>
                ),
                ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                li: ({ children }) => <li className="ml-2">{children}</li>,
                h1: ({ children }) => <h1 className="text-xl font-bold mb-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-semibold mb-2">{children}</h2>,
                h3: ({ children }) => <h3 className="text-base font-semibold mb-1">{children}</h3>,
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-white/20 pl-4 italic my-2">
                    {children}
                  </blockquote>
                ),
                a: ({ children, href }) => (
                  <a href={href} className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noopener noreferrer">
                    {children}
                  </a>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-4">
                    <table className="min-w-full border-collapse border border-white/20">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-white/10">{children}</thead>
                ),
                tbody: ({ children }) => (
                  <tbody className="divide-y divide-white/10">{children}</tbody>
                ),
                tr: ({ children }) => (
                  <tr className="border-b border-white/10">{children}</tr>
                ),
                th: ({ children }) => (
                  <th className="px-4 py-2 text-left font-semibold text-white/90 border border-white/20">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-4 py-2 text-white/70 border border-white/20">
                    {children}
                  </td>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        <span className="text-xs text-white/40 px-1">
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white flex items-center justify-center">
          <User className="w-4 h-4 text-black" />
        </div>
      )}
    </div>
  );
}

