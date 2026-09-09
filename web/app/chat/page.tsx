import { ChatWorkspace } from "@/components/chat/chat-workspace";
import { SiteHeader } from "@/components/site-header";

export default function ChatPage() {
  return (
    <div className="flex h-svh flex-col overflow-hidden bg-[var(--paper)]">
      <SiteHeader />
      <main className="flex min-h-0 flex-1 flex-col">
        <ChatWorkspace />
      </main>
    </div>
  );
}
