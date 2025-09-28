const API_BASE_URL = '/api/chat';

export interface ChatMessagePayload {
  role: 'user' | 'assistant';
  text: string;
  meta?: any;
}

export interface ChatMessage extends ChatMessagePayload {
  id: number;
  created_at: string;
}

export async function createConversation(title?: string): Promise<{ id: number }> {
  const url = new URL(`${API_BASE_URL}/conversations`, window.location.origin);
  if (title) url.searchParams.set('title', title);
  const res = await fetch(url.toString().replace(window.location.origin, ''), { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create conversation');
  return res.json();
}

export async function listMessages(conversationId: number): Promise<ChatMessage[]> {
  const res = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`);
  if (!res.ok) throw new Error('Failed to load messages');
  return res.json();
}

export async function appendMessage(conversationId: number, payload: ChatMessagePayload): Promise<ChatMessage> {
  const res = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to save message');
  return res.json();
}

export interface RoutedResponse {
  route: 'text2sql' | 'llm';
  answer?: string;
  sql?: string;
  result?: any;
  formatted_result?: string;
  presentation?: string;
}

export async function routeChat(conversationId: number, message: string): Promise<RoutedResponse> {
  const res = await fetch(`${API_BASE_URL}/route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, message })
  });
  if (!res.ok) throw new Error('Failed to route chat');
  return res.json();
}


