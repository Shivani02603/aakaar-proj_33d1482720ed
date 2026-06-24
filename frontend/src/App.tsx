import { useState } from 'react';
import ChatWindow from '@/components/ChatWindow';
import DocumentUploader from '@/components/DocumentUploader';
import SessionSidebar from '@/components/SessionSidebar';

export default function AppLayout() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="flex items-center justify-between px-6 py-4 bg-gray-800 text-white">
        <h1 className="text-lg font-bold">Aakaar Project</h1>
        <button
          onClick={() => setActiveSessionId(null)}
          className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded"
        >
          New Chat
        </button>
      </header>
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-64 bg-gray-100 border-r border-gray-300 flex flex-col">
          <SessionSidebar onSelectSession={handleSelectSession} />
          <div className="flex-1 overflow-y-auto">
            <DocumentUploader sessionId={activeSessionId} />
          </div>
        </aside>
        <main className="flex-1 flex flex-col">
          <ChatWindow activeSessionId={activeSessionId} />
        </main>
      </div>
    </div>
  );
}