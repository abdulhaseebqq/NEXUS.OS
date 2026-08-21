import { useState } from "react"
import type {
  FormEvent,
} from "react"
import {
  FaPaperPlane,
  FaRobot,
} from "react-icons/fa"

function ChatPage() {
  const [message, setMessage] =
    useState("")

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!message.trim()) {
      return
    }

    setMessage("")
  }

  return (
    <main className="chat-page">
      <section className="chat-header">
        <div className="chat-ai-icon">
          <FaRobot />
        </div>

        <div>
          <span>NEXUS AI</span>
          <h1>Conversation</h1>
          <p>
            AI engine integration is the next sprint.
          </p>
        </div>
      </section>

      <section className="chat-window">
        <div className="chat-empty-state">
          <FaRobot />

          <h2>
            How can NEXUS help you?
          </h2>

          <p>
            This interface is ready for the AI backend
            integration.
          </p>
        </div>

        <form
          className="chat-composer"
          onSubmit={handleSubmit}
        >
          <textarea
            value={message}
            onChange={(event) =>
              setMessage(
                event.target.value,
              )
            }
            placeholder="Message NEXUS..."
            rows={1}
          />

          <button
            type="submit"
            aria-label="Send message"
          >
            <FaPaperPlane />
          </button>
        </form>
      </section>
    </main>
  )
}

export default ChatPage