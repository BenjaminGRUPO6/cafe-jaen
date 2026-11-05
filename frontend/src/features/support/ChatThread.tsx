import { useState, type FormEvent } from "react";
import type { ApiError } from "../../shared/api/client";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDateTime } from "../../shared/format";
import { texts } from "../../shared/texts/es";
import { MAX_LENGTH, type SupportMessage } from "./support";

/**
 * Conversación tipo chat: los mensajes de `mine` a la derecha y los de la otra parte a la
 * izquierda, con la caja para escribir debajo. La usan el caficultor y el equipo.
 */
export function ChatThread({
  messages,
  mine,
  placeholder,
  onSend,
}: {
  messages: SupportMessage[];
  mine: SupportMessage["author"];
  placeholder: string;
  onSend: (text: string) => Promise<void>;
}) {
  const [text, setText] = useState("");
  const [error, setError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onSend(text);
      setText("");
    } catch (caught) {
      setError(caught as ApiError);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="chat">
      {messages.length === 0 ? (
        <p className="muted chat__empty">{texts.support.empty}</p>
      ) : (
        <ol className="chat__list" aria-live="polite">
          {messages.map((m) => (
            <li
              key={m.id}
              className={`chat__bubble ${m.author === mine ? "chat__bubble--mine" : ""}`}
            >
              <span className="chat__author">{texts.support.authors[m.author]}</span>
              <p className="chat__text">{m.text}</p>
              <small className="chat__time">{formatDateTime(new Date(m.created_at))}</small>
            </li>
          ))}
        </ol>
      )}
      <form className="form card chat__form" onSubmit={submit}>
        <label>
          <span className="sr-only">{placeholder}</span>
          <textarea
            rows={3}
            maxLength={MAX_LENGTH}
            placeholder={placeholder}
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
          />
        </label>
        <StatusMessage error={error} />
        <button className="button" disabled={busy || text.trim() === ""}>
          {texts.support.send}
        </button>
      </form>
    </div>
  );
}
