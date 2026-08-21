import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react"
import type {
  FormEvent,
  KeyboardEvent,
} from "react"
import {
  FaBars,
  FaComments,
  FaPaperPlane,
  FaPlus,
  FaRobot,
  FaXmark,
} from "react-icons/fa6"

import {
  createConversation,
  getConversation,
  listConversations,
  sendMessage,
} from "../../services/chat"
import type {
  ChatConversation,
  ChatMessage,
} from "../../types/chat"

import "./ChatPage.css"

function ChatPage() {
  const [
    conversations,
    setConversations,
  ] = useState<ChatConversation[]>([])

  const [
    activeConversationId,
    setActiveConversationId,
  ] = useState<number | null>(null)

  const [messages, setMessages] =
    useState<ChatMessage[]>([])

  const [message, setMessage] =
    useState("")

  const [isLoading, setIsLoading] =
    useState(false)

  const [isHistoryOpen, setIsHistoryOpen] =
    useState(false)

  const [error, setError] =
    useState("")

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null)

  const loadConversations =
    useCallback(async () => {
      try {
        const response =
          await listConversations()

        setConversations(response.data)
      } catch {
        setError(
          "Unable to load conversations.",
        )
      }
    }, [])

  useEffect(() => {
    void loadConversations()
  }, [loadConversations])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    })
  }, [messages, isLoading])

  async function handleNewConversation() {
    try {
      setError("")

      const response =
        await createConversation()

      const conversation =
        response.data

      setConversations(
        (current) => [
          conversation,
          ...current,
        ],
      )

      setActiveConversationId(
        conversation.id,
      )

      setMessages([])

      setIsHistoryOpen(false)
    } catch {
      setError(
        "Unable to create conversation.",
      )
    }
  }

  async function handleOpenConversation(
    conversationId: number,
  ) {
    try {
      setError("")

      const response =
        await getConversation(
          conversationId,
        )

      setActiveConversationId(
        conversationId,
      )

      setMessages(
        response.data.messages,
      )

      setIsHistoryOpen(false)
    } catch {
      setError(
        "Unable to open conversation.",
      )
    }
  }

  async function submitMessage() {
    const trimmedMessage =
      message.trim()

    if (
      !trimmedMessage ||
      isLoading
    ) {
      return
    }

    try {
      setIsLoading(true)
      setError("")

      let conversationId =
        activeConversationId

      if (!conversationId) {
        const conversationResponse =
          await createConversation()

        conversationId =
          conversationResponse.data.id

        setActiveConversationId(
          conversationId,
        )

        setConversations(
          (current) => [
            conversationResponse.data,
            ...current,
          ],
        )
      }

      setMessage("")

      const response =
        await sendMessage(
          conversationId,
          trimmedMessage,
        )

      setMessages(
        (current) => [
          ...current,
          response.data.user_message,
          response.data.assistant_message,
        ],
      )

      await loadConversations()
    } catch {
      setError(
        "NEXUS could not process your message.",
      )
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    await submitMessage()
  }

  function handleComposerKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>,
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault()

      void submitMessage()
    }
  }

  return (
    <main className="nexus-chat-page">
      <aside
        className={
          isHistoryOpen
            ? "nexus-chat-history nexus-chat-history-open"
            : "nexus-chat-history"
        }
      >
        <div className="nexus-history-header">
          <div>
            <span className="nexus-history-label">
              NEXUS HISTORY
            </span>

            <h2>Conversations</h2>
          </div>

          <button
            type="button"
            className="nexus-history-close"
            aria-label="Close history"
            onClick={() =>
              setIsHistoryOpen(false)
            }
          >
            <FaXmark />
          </button>
        </div>

        <button
          type="button"
          className="nexus-new-chat-button"
          onClick={
            handleNewConversation
          }
        >
          <FaPlus />

          <span>New chat</span>
        </button>

        <div className="nexus-conversation-list">
          {conversations.length === 0 ? (
            <div className="nexus-history-empty">
              <FaComments />

              <span>
                No conversations yet
              </span>

              <small>
                Start talking with NEXUS.
              </small>
            </div>
          ) : (
            conversations.map(
              (conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  className={
                    conversation.id ===
                    activeConversationId
                      ? "nexus-conversation-open nexus-conversation-active"
                      : "nexus-conversation-open"
                  }
                  onClick={() =>
                    handleOpenConversation(
                      conversation.id,
                    )
                  }
                >
                  <FaComments />

                  <span>
                    {conversation.title}
                  </span>
                </button>
              ),
            )
          )}
        </div>
      </aside>

      {isHistoryOpen && (
        <button
          type="button"
          className="nexus-history-backdrop"
          aria-label="Close history"
          onClick={() =>
            setIsHistoryOpen(false)
          }
        />
      )}

      <section className="nexus-chat-main">
        <header className="nexus-chat-topbar">
          <div className="nexus-chat-title-group">
            <button
              type="button"
              className="nexus-history-toggle"
              aria-label="Open conversation history"
              onClick={() =>
                setIsHistoryOpen(true)
              }
            >
              <FaBars />
            </button>

            <div className="nexus-chat-logo">
              <FaRobot />
            </div>

            <div>
              <span>NEXUS AI</span>

              <h1>
                {activeConversationId
                  ? "Conversation"
                  : "New conversation"}
              </h1>
            </div>
          </div>

          <div className="nexus-ai-status">
            <span />
            Online
          </div>
        </header>

        {error && (
          <div
            className="nexus-chat-error"
            role="alert"
          >
            {error}
          </div>
        )}

        <div className="nexus-chat-body">
          {messages.length === 0 ? (
            <div className="nexus-chat-welcome">
              <div className="nexus-welcome-logo">
                <FaRobot />
              </div>

              <h2>
                How can I help you?
              </h2>

              <p>
                Ask NEXUS anything or start
                working on a task.
              </p>

              <div className="nexus-prompt-suggestions">
                <button
                  type="button"
                  onClick={() =>
                    setMessage(
                      "Help me plan my day",
                    )
                  }
                >
                  Plan my day
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setMessage(
                      "Help me write some code",
                    )
                  }
                >
                  Write code
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setMessage(
                      "Explain something to me",
                    )
                  }
                >
                  Explain something
                </button>
              </div>
            </div>
          ) : (
            <div className="nexus-message-list">
              {messages.map(
                (chatMessage) => (
                  <article
                    key={chatMessage.id}
                    className={
                      chatMessage.role ===
                      "user"
                        ? "nexus-message nexus-message-user"
                        : "nexus-message nexus-message-ai"
                    }
                  >
                    <div className="nexus-message-avatar">
                      {chatMessage.role ===
                      "user"
                        ? "You"
                        : "N"}
                    </div>

                    <div className="nexus-message-content">
                      <strong>
                        {chatMessage.role ===
                        "user"
                          ? "You"
                          : "NEXUS"}
                      </strong>

                      <p>
                        {chatMessage.content}
                      </p>
                    </div>
                  </article>
                ),
              )}

              {isLoading && (
                <article className="nexus-message nexus-message-ai">
                  <div className="nexus-message-avatar">
                    N
                  </div>

                  <div className="nexus-message-content">
                    <strong>
                      NEXUS
                    </strong>

                    <div className="nexus-thinking">
                      <span />
                      <span />
                      <span />
                    </div>
                  </div>
                </article>
              )}

              <div
                ref={messagesEndRef}
              />
            </div>
          )}
        </div>

        <div className="nexus-composer-wrapper">
          <form
            className="nexus-chat-composer"
            onSubmit={handleSubmit}
          >
            <textarea
              value={message}
              onChange={(event) =>
                setMessage(
                  event.target.value,
                )
              }
              onKeyDown={
                handleComposerKeyDown
              }
              placeholder="Message NEXUS..."
              rows={1}
              disabled={isLoading}
            />

            <button
              type="submit"
              aria-label="Send message"
              disabled={
                isLoading ||
                !message.trim()
              }
            >
              <FaPaperPlane />
            </button>
          </form>

          <p className="nexus-composer-hint">
            Enter to send · Shift + Enter
            for new line
          </p>
        </div>
      </section>
    </main>
  )
}

export default ChatPage