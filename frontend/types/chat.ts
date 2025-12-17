export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sql?: string;
  data?: any[];
  chartImage?: string; // base64 encoded image
}

export interface ChatResponse {
  question: string;
  generated_sql: string;
  data: any[];
  answer: string;
  chart_image?: string;
  status: "success" | "error";
  error?: string;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

