import { AnimatePresence, motion } from "framer-motion";
import { useState, type FormEvent } from "react";
import { api, ApiError } from "../../shared/api/client";
import type { AdvisorAnswer } from "../../shared/api/types";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { texts } from "../../shared/texts/es";

interface ChatMessage {
  id: number;
  author: "user" | "advisor";
  text: string;
}

// Cada mensaje nuevo entra desde su lado (respuesta visible a la acción del caficultor)
const bubbleMotion = {
  initial: { opacity: 0, y: 10, scale: 0.97 },
  animate: { opacity: 1, y: 0, scale: 1 },
  transition: { type: "spring" as const, stiffness: 380, damping: 28 },
};

/** HU08: conversación con el Agente Asesor. */
export function AdvisorPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(false);

  const ask = async (text: string) => {
    if (!text.trim()) return;
    setMessages((current) => [...current, { id: current.length, author: "user", text }]);
    setQuestion("");
    setLoading(true);
    setError(null);
    try {
      const reply = await api.post<AdvisorAnswer>("/advisor/ask", { question: text });
      setMessages((current) => [
        ...current,
        { id: current.length, author: "advisor", text: reply.answer },
      ]);
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
            <motion.button
              key={example}
              className="chip"
              whileTap={{ scale: 0.95 }}
              onClick={() => void ask(example)}
            >
              {example}
            </motion.button>
          ))}
        </div>
      )}
      <div className="chat" aria-live="polite">
        {messages.map((message) => (
          <motion.p
            key={message.id}
            className={`bubble bubble--${message.author}`}
            {...bubbleMotion}
          >
            {message.text}
          </motion.p>
        ))}
        <AnimatePresence>
          {loading && (
            <motion.p
              className="bubble bubble--advisor typing"
              aria-label={texts.common.loading}
              {...bubbleMotion}
              exit={{ opacity: 0 }}
            >
              {[0, 1, 2].map((dot) => (
                <motion.span
                  key={dot}
                  animate={{ y: [0, -5, 0] }}
                  transition={{ repeat: Infinity, duration: 0.8, delay: dot * 0.15 }}
                />
              ))}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
      <StatusMessage error={error} />
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
