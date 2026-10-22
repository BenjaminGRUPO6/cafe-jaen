import { useState, type FormEvent } from "react";
import { api, ApiError } from "../../shared/api/client";
import type { AdvisorAnswer } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { texts } from "../../shared/texts/es";

interface ChatMessage {
  author: "user" | "advisor";
  text: string;
}

/** HU08: conversación con el Agente Asesor. */
export function AdvisorPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(false);

  const ask = async (text: string) => {
    if (!text.trim()) return;
    setMessages((current) => [...current, { author: "user", text }]);
    setQuestion("");
    setLoading(true);
    setError(null);
    try {
      const reply = await api.post<AdvisorAnswer>("/advisor/ask", { question: text });
      setMessages((current) => [...current, { author: "advisor", text: reply.answer }]);
    } catch (caught) {
      setError(caught as ApiError);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    void ask(question);
  };

  return (
    <section>
      <h1>{texts.advisor.title}</h1>
      {messages.length === 0 && (
        <div className="chips">
          {texts.advisor.examples.map((example) => (
            <button key={example} className="chip" onClick={() => void ask(example)}>
              {example}
            </button>
          ))}
        </div>
      )}
      <div className="chat" aria-live="polite">
        {messages.map((message, index) => (
          <p key={index} className={`bubble bubble--${message.author}`}>
            {message.text}
          </p>
        ))}
      </div>
      <StatusMessage loading={loading} error={error} />
      <form className="form" onSubmit={onSubmit}>
        <textarea
          rows={2}
          maxLength={500}
          placeholder={texts.advisor.placeholder}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button className="button" disabled={loading || !question.trim()}>
          {texts.advisor.send}
        </button>
      </form>
    </section>
  );
}
