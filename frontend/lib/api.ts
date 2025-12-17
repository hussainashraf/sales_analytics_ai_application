import { ChatResponse } from "@/types/chat";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendChatMessage(
  question: string,
  stream: boolean = true,
  documentMode: boolean = false,
  onChunk?: (chunk: string, eventType?: string) => void,
  onMetadata?: (metadata: { sql: string; data: any[] }) => void,
  onStatus?: (status: { step: string; message: string }) => void,
  onChart?: (chartBase64: string) => void
): Promise<ChatResponse> {
  if (stream) {
    // Streaming response
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question, stream: true, document_mode: documentMode }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let sql = "";
    let responseData: any[] = [];
    let answer = "";
    let chartImage: string | undefined;

    if (!reader) {
      throw new Error("No response body");
    }

    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === "status") {
              // Status update (what AI is doing)
              if (onStatus) {
                onStatus({ step: data.step, message: data.message });
              }
            } else if (data.type === "sql_chunk") {
              // SQL is being generated (streaming)
              sql += data.content;
              if (onChunk) {
                onChunk(data.content, "sql_chunk");
              }
            } else if (data.type === "sql_complete") {
              // SQL generation complete
              sql = data.sql || sql;
              if (onMetadata) {
                onMetadata({ sql, data: [] });
              }
            } else if (data.type === "sql_result") {
              // SQL execution results
              responseData = data.data || [];
              if (onMetadata) {
                onMetadata({ sql, data: responseData });
              }
            } else if (data.type === "chart_image") {
              // Chart image received
              chartImage = data.image;
              if (onChart) {
                onChart(data.image);
              }
            } else if (data.type === "chart_error") {
              console.warn("Chart generation failed:", data.error);
            } else if (data.type === "sql_error") {
              // SQL execution error
              throw new Error(data.error || "SQL execution failed");
            } else if (data.type === "answer_chunk") {
              // Answer is being generated (streaming)
              answer += data.content;
              if (onChunk) {
                onChunk(data.content, "answer_chunk");
              }
            } else if (data.type === "metadata") {
              // Legacy metadata format
              sql = data.sql || "";
              responseData = data.data || [];
              if (onMetadata) {
                onMetadata({ sql, data: responseData });
              }
            } else if (data.type === "chunk") {
              // Legacy chunk format
              answer += data.content;
              if (onChunk) {
                onChunk(data.content, "answer_chunk");
              }
            } else if (data.type === "done") {
              // Streaming complete
            } else if (data.type === "error") {
              throw new Error(data.error || "Unknown error");
            }
          } catch (e) {
            // Skip invalid JSON
            console.warn("Failed to parse SSE data:", e);
          }
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      const line = buffer.trim();
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === "chunk") {
            answer += data.content;
            if (onChunk) {
              onChunk(data.content);
            }
          }
        } catch (e) {
          // Skip invalid JSON
        }
      }
    }

    return {
      question,
      generated_sql: sql,
      data: responseData,
      answer,
      chart_image: chartImage,
      status: "success",
    };
  } else {
    // Non-streaming response
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question, stream: false, document_mode: documentMode }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }
}

