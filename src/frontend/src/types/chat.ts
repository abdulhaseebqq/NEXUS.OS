export type ChatConversation = {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export type ChatMessage = {
  id: number
  conversation_id: number
  role: "user" | "assistant"
  content: string
  created_at: string
}

export type ConversationDetail = {
  conversation: ChatConversation
  messages: ChatMessage[]
}

export type SendMessageData = {
  conversation: ChatConversation
  user_message: ChatMessage
  assistant_message: ChatMessage
}

export type ApiSuccess<T> = {
  success: true
  message: string
  data: T
}