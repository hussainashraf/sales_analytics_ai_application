# Sales Analytics Chat Frontend

A beautiful, modular chatbot UI built with Next.js, shadcn/ui, and Tailwind CSS.

## Features

- 🎨 Beautiful, modern UI with shadcn components
- 💬 Real-time chat interface
- 📊 Displays SQL queries and results
- 🌙 Dark mode support
- 📱 Responsive design
- ⚡ Fast and performant

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main page with ChatInterface
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── ui/               # shadcn UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── card.tsx
│   └── chat/             # Chat-specific components
│       ├── chat-interface.tsx  # Main chat container
│       ├── message-bubble.tsx  # Individual message component
│       └── chat-input.tsx      # Input component
├── lib/
│   ├── api.ts            # API client
│   └── utils.ts          # Utility functions
└── types/
    └── chat.ts           # TypeScript types
```

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure API URL:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local and set NEXT_PUBLIC_API_URL to your backend URL
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Components

### ChatInterface
Main container component that manages chat state and API calls.

### MessageBubble
Displays individual messages with:
- User/Assistant avatars
- Message content
- Generated SQL (if available)
- Query results (if available)
- Timestamps

### ChatInput
Input component with:
- Send button
- Loading state
- Keyboard shortcuts (Enter to send)

## API Integration

The frontend communicates with the FastAPI backend at `/chat` endpoint:

```typescript
POST /chat
Body: { question: string }
Response: {
  question: string;
  generated_sql: string;
  data: any[];
  answer: string;
  status: "success" | "error";
}
```

## Styling

Uses Tailwind CSS with shadcn/ui components. Supports:
- Light and dark themes
- Responsive breakpoints
- Smooth animations
- Custom color scheme

## Development

- **TypeScript**: Full type safety
- **ESLint**: Code quality
- **Modular**: Easy to extend and maintain
