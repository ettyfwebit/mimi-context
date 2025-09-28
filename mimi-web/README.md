# Mimi Web

A modern React frontend for the Mimi knowledge base system. Provides intelligent search, AI chat, and administrative tools for managing your documents and system health.

## Features

### 🔍 Search

- **Intelligent search** with ranked results and confidence scores
- **Smart snippets** with keyword highlighting
- **Source citations** with clickable links
- **Filtering** by source and other criteria
- **Low confidence warnings** with helpful suggestions

### 💬 Chat (Optional)

- **AI-powered conversations** with source citations
- **Inline source references** with clickable markers
- **Model selection** for different AI capabilities
- **Raw chunks debug view** for development

### 🛠️ Studio

- **File upload** with drag-and-drop support
- **Document management** with filtering and search
- **Event monitoring** with status tracking
- **Health monitoring** and configuration display

### 🎨 User Experience

- **Dark mode** support with system preference detection
- **Responsive design** for mobile and desktop
- **Keyboard shortcuts** (/ to focus search, ⌘+Enter to submit)
- **Loading states** and error handling
- **Accessibility** features with proper ARIA labels

## Quick Start

### 1. Installation

```bash
npm install
```

### 2. Environment Configuration

Copy the environment template:

```bash
cp .env.example .env.local
```

Edit `.env.local` and set your backend URL:

```env
VITE_MIMI_API_BASE=http://localhost:8080
```

### 3. Development

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### 4. Build for Production

```bash
npm run build
npm run preview
```

## Environment Variables

| Variable                         | Required | Default | Description                           |
| -------------------------------- | -------- | ------- | ------------------------------------- |
| `VITE_MIMI_API_BASE`             | ✅       | -       | Backend API base URL                  |
| `VITE_MIMI_API_KEY`              | ❌       | -       | API key for authentication            |
| `VITE_MIMI_DEFAULT_TOP_K`        | ❌       | `5`     | Default number of search results      |
| `VITE_MIMI_DEFAULT_MODEL`        | ❌       | -       | Default AI model for chat             |
| `VITE_MIMI_CONFIDENCE_THRESHOLD` | ❌       | `0.30`  | Threshold for low confidence warnings |

## Backend API Requirements

This frontend expects the following endpoints from your Mimi Core backend:

### Required Endpoints

- `POST /rag/query` - Retrieve search results
- `POST /ingest/upload` - Upload documents
- `GET /admin/docs` - List documents
- `GET /admin/updates` - List ingestion events
- `GET /health` - Health check

### Optional Endpoints

- `POST /agent/ask` - AI chat (enables Chat page)

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: TanStack Query (React Query)
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **UI Components**: Custom components with Headless UI
- **Notifications**: React Hot Toast

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI primitives (Button, Input, etc.)
│   ├── layout/         # Layout components (Navigation, Layout)
│   └── features/       # Feature-specific components
│       ├── search/     # Search functionality
│       ├── chat/       # Chat functionality
│       └── studio/     # Admin studio functionality
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API services and HTTP client
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── test/               # Test setup and utilities
```

## Keyboard Shortcuts

- **`/`** - Focus search input
- **`⌘/Ctrl + Enter`** - Submit form (search or chat)

## Testing

Run tests:

```bash
npm test
```

Run tests with UI:

```bash
npm run test:ui
```

## Code Quality

Format code:

```bash
npm run format
```

Lint code:

```bash
npm run lint
npm run lint:fix
```

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+

## Contributing

1. Follow the existing code style and conventions
2. Write tests for new functionality
3. Ensure all tests pass before submitting
4. Use TypeScript for type safety
5. Follow accessibility best practices

## License

MIT License - see LICENSE file for details.
