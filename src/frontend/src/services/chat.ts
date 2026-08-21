import { apiRequest } from "./api"

import type {
  ApiSuccess,
  ChatConversation,
  ConversationDetail,
  SendMessageData,
} from "../types/chat"

function authenticatedHeaders() {
  const accessToken =
    sessionStorage.getItem(
      "nexus_access_token",
    )

  if (!accessToken) {
    throw new Error(
      "Authentication token is missing.",
    )
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  }
}

export function createConversation(
  title?: string,
) {
  return apiRequest<
    ApiSuccess<ChatConversation>
  >("/chat/conversations", {
    method: "POST",
    headers: authenticatedHeaders(),
    body: JSON.stringify({
      title,
    }),
  })
}

export function listConversations() {
  return apiRequest<
    ApiSuccess<ChatConversation[]>
  >("/chat/conversations", {
    headers: authenticatedHeaders(),
  })
}

export function getConversation(
  conversationId: number,
) {
  return apiRequest<
    ApiSuccess<ConversationDetail>
  >(
    `/chat/conversations/${conversationId}`,
    {
      headers: authenticatedHeaders(),
    },
  )
}

export function sendMessage(
  conversationId: number,
  content: string,
) {
  return apiRequest<
    ApiSuccess<SendMessageData>
  >(
    `/chat/conversations/${conversationId}/messages`,
    {
      method: "POST",
      headers: authenticatedHeaders(),
      body: JSON.stringify({
        content,
      }),
    },
  )
}

export function deleteConversation(
  conversationId: number,
) {
  return apiRequest<ApiSuccess<null>>(
    `/chat/conversations/${conversationId}`,
    {
      method: "DELETE",
      headers: authenticatedHeaders(),
    },
  )
}