import { api } from "../../shared/api/client";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { useApi } from "../../shared/hooks/useApi";
import { useAutoReload } from "../../shared/hooks/useAutoReload";
import { texts } from "../../shared/texts/es";
import { ChatThread } from "./ChatThread";
import type { SupportMessage } from "./support";

const REFRESH_MS = 15_000; // la respuesta del equipo aparece sola

/** «Atención»: el caficultor escribe sus dudas al equipo y ve las respuestas. */
export function SupportPage() {
  const { data, error, reload } = useApi<{ messages: SupportMessage[] }>("/support/messages");
  useAutoReload(reload, REFRESH_MS);

  const send = async (text: string) => {
    await api.post("/support/messages", { text });
    reload();
  };

  return (
    <section>
      <h1>{texts.support.title}</h1>
      <p className="muted">{texts.support.intro}</p>
      {data ? (
        <ChatThread
          messages={data.messages}
          mine="farmer"
          placeholder={texts.support.placeholder}
          onSend={send}
        />
      ) : (
        <StatusMessage loading={!error} error={error} onRetry={reload} />
      )}
    </section>
  );
}
