import { useSearchParams } from "react-router-dom";
import { api } from "../../shared/api/client";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDateTime } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { useAutoReload } from "../../shared/hooks/useAutoReload";
import { texts } from "../../shared/texts/es";
import { AdminTabs } from "../admin/AdminTabs";
import { ChatThread } from "./ChatThread";
import { preview, type SupportMessage, type SupportThread, type SupportUser } from "./support";

const REFRESH_MS = 15_000;

/** Solo el equipo: bandeja de «Atención» y respuesta a cada caficultor. */
export function SupportInboxPage() {
  const [params, setParams] = useSearchParams();
  const selected = params.get("usuario");
  const inbox = useApi<{ unread: number; threads: SupportThread[] }>("/admin/support");
  useAutoReload(inbox.reload, REFRESH_MS);

  return (
    <section>
      <AdminTabs />
      <h1>{texts.support.inboxTitle}</h1>
      <p className="muted">{texts.support.inboxIntro}</p>
      {selected ? (
        <Conversation
          userId={selected}
          onBack={() => {
            setParams({});
            inbox.reload();
          }}
        />
      ) : inbox.data ? (
        inbox.data.threads.length === 0 ? (
          <p className="card muted">{texts.support.inboxEmpty}</p>
        ) : (
          <ul className="inbox">
            {inbox.data.threads.map((t) => (
              <li key={t.user_id}>
                <button
                  type="button"
                  className={`inbox__item ${t.unread > 0 ? "inbox__item--unread" : ""}`}
                  onClick={() => setParams({ usuario: t.user_id })}
                >
                  <span className="inbox__top">
                    <strong>{who(t.user)}</strong>
                    {t.unread > 0 && <span className="badge">{t.unread}</span>}
                  </span>
                  <span className="inbox__preview">
                    {t.last_author === "team" && `${texts.support.you}: `}
                    {preview(t.last_text)}
                  </span>
                  <small>{formatDateTime(new Date(t.last_at))}</small>
                </button>
              </li>
            ))}
          </ul>
        )
      ) : (
        <StatusMessage loading={!inbox.error} error={inbox.error} onRetry={inbox.reload} />
      )}
    </section>
  );
}

function Conversation({ userId, onBack }: { userId: string; onBack: () => void }) {
  const { data, error, reload } = useApi<{ user: SupportUser | null; messages: SupportMessage[] }>(
    `/admin/support/${userId}`,
  );
  useAutoReload(reload, REFRESH_MS);

  const reply = async (text: string) => {
    await api.post(`/admin/support/${userId}`, { text });
    reload();
  };

  return (
    <div>
      <button type="button" className="link-button inbox__back" onClick={onBack}>
        ← {texts.support.back}
      </button>
      {data ? (
        <>
          <h2 className="inbox__who">{who(data.user)}</h2>
          {data.user?.email && <p className="muted">{data.user.email}</p>}
          <ChatThread
            messages={data.messages}
            mine="team"
            placeholder={texts.support.replyPlaceholder}
            onSend={reply}
          />
        </>
      ) : (
        <StatusMessage loading={!error} error={error} onRetry={reload} />
      )}
    </div>
  );
}

function who(user: SupportUser | null): string {
  return user ? user.phone : texts.support.deletedAccount;
}
