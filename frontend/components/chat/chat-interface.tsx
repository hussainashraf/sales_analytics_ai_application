"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/types/chat";
import { MessageBubble } from "./message-bubble";
import { ChatInput } from "./chat-input";
import { ChatHeader } from "./header";
import { WelcomeScreen } from "./welcome-screen";
import { Sidebar } from "@/components/ui/sidebar";
import { StatusIndicator } from "./status-indicator";
import { sendChatMessage } from "@/lib/api";
import { AlertCircle, FileText } from "lucide-react";

type StatusStep = "generating_sql" | "executing_sql" | "generating_answer" | "generating_chart" | null;

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStatus, setCurrentStatus] = useState<{ step: "generating_sql" | "executing_sql" | "generating_answer" | "generating_chart"; message: string } | null>(null);
  const [documentMode, setDocumentMode] = useState(false); // Toggle for document analysis
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNewChat = () => {
    setMessages([]);
    setError(null);
  };

  const handleSendMessage = async (question: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    
    // Set initial status based on mode
    if (documentMode) {
      setCurrentStatus({ step: "generating_answer", message: "Analyzing documents..." });
    } else {
      setCurrentStatus({ step: "generating_sql", message: "Generating SQL query..." });
    }

    // Create placeholder for streaming message
    const assistantMessageId = (Date.now() + 1).toString();
    let currentSql = "";
    let currentData: any[] = [];
    let sqlComplete = false;

    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const response = await sendChatMessage(
        question,
        true,
        documentMode, // Pass document mode to API
        (chunk, eventType) => {
          if (eventType === "sql_chunk") {
            // SQL is being generated (streaming)
            currentSql += chunk;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, sql: currentSql }
                  : msg
              )
            );
          } else if (eventType === "answer_chunk") {
            // Answer is being generated (streaming)
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: msg.content + chunk }
                  : msg
              )
            );
          }
        },
        (metadata) => {
          // Metadata callback - SQL complete or data received
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, sql: metadata.sql || msg.sql, data: metadata.data || msg.data }
                : msg
            )
          );
        },
        (status) => {
          // Status updates - show what AI is doing
          if (status.step === "generating_sql" || status.step === "executing_sql" || status.step === "generating_answer" || status.step === "generating_chart") {
            setCurrentStatus(status as { step: "generating_sql" | "executing_sql" | "generating_answer" | "generating_chart"; message: string });
          }
        },
        (chartBase64) => {
          // Chart image received
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, chartImage: chartBase64 }
                : msg
            )
          );
        }
      );

      if (response.status === "error") {
        throw new Error(response.error || "An error occurred");
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get response";
      setError(errorMessage);

      // Update the placeholder message with error
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: `Sorry, I encountered an error: ${errorMessage}`,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
      setCurrentStatus(null);
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0a0a] text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar onNewChat={handleNewChat} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <ChatHeader />

        {/* Mode Toggle */}
        <div className="px-6 py-3 border-b border-gray-800/50 bg-[#0a0a0a]">
          <div className="max-w-3xl mx-auto flex items-center gap-3">
            <button
              onClick={() => setDocumentMode(!documentMode)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                documentMode
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Document Analysis</span>
            </button>
            <span className="text-sm text-gray-500">
              {documentMode 
                ? "Analyzing Purchase Orders & Proforma Invoices" 
                : "Querying Sales Database"}
            </span>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto bg-[#0a0a0a]">
          {messages.length === 0 ? (
            <WelcomeScreen />
          ) : (
            <div className="max-w-3xl mx-auto py-6">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {currentStatus && currentStatus.step && (
                <StatusIndicator step={currentStatus.step} message={currentStatus.message} />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mx-4 mb-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Input Area */}
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={!!error}
        />
      </div>
    </div>
  );
}

