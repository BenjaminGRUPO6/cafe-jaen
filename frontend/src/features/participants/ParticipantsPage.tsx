import { motion } from "framer-motion";
import { useState } from "react";
import { api, ApiError } from "../../shared/api/client";
import { ConfirmButton } from "../../shared/components/ConfirmButton";
import { StatusMessage } from "../../shared/components/StatusMessage";
import { formatDateTime } from "../../shared/format";
import { useApi } from "../../shared/hooks/useApi";
import { useAutoReload } from "../../shared/hooks/useAutoReload";
import { TrashIcon } from "../../shared/motion/icons";
import { texts } from "../../shared/texts/es";
import { AdminTabs } from "../admin/AdminTabs";
import { startOfToday, summarize, type Participant, type ParticipantsReport } from "./participants";

const REFRESH_MS = 10_000; // un registro nuevo aparece en menos de 10 s sin recargar

/** Solo el equipo: quiénes del GE se registraron, con qué código y cuándo entraron. */
export function ParticipantsPage() {
  const { data, error, reload } = useApi<ParticipantsReport>("/admin/participants");
  useAutoReload(reload, REFRESH_MS);
  const result = data ? summarize(data, startOfToday(new Date())) : null;
  const [actionError, setActionError] = useState<ApiError | null>(null);

  // Elimina una cuenta (por ejemplo, con datos inventados); su código queda libre otra vez
  const remove = async (participant: Participant) => {
    setActionError(null);
    try {
      await api.delete(`/admin/participants/${participant.id}`);
      reload();
    } catch (caught) {
      setActionError(caught as ApiError);
    }
  };

  return (
    <section>
      <AdminTabs />
      <h1>{texts.participants.title}</h1>
      <p className="muted">
        <motion.span
          className="pill__dot participants__pulse"
          animate={{ opacity: [1, 0.2, 1] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
          aria-hidden="true"
        />{" "}
        {texts.participants.intro}
      </p>
      <StatusMessage error={actionError} />
      {data && result ? (
        <>
          <div className="stats">
            <Stat label={texts.participants.registered} value={String(result.farmers.length)} />
            <Stat
              label={texts.participants.codes}
              value={`${data.codes.used} / ${data.codes.total}`}
            />
            <Stat label={texts.participants.activeToday} value={String(result.activeSince)} />
          </div>
          {result.farmers.length === 0 ? (
            <p className="card muted">{texts.participants.empty}</p>
          ) : (
            <ul className="participants" aria-live="polite">
              {result.farmers.map((p) => (
                <ParticipantRow key={p.id} participant={p} onDelete={remove} />
              ))}
            </ul>
          )}
          <h2 className="participants__team">{texts.participants.team}</h2>
          <ul className="participants">
            {result.team.map((p) => (
              <ParticipantRow key={p.id} participant={p} onDelete={remove} />
            ))}
          </ul>
        </>
      ) : (
        <StatusMessage loading={!error} error={error} />
      )}
    </section>
  );
}

function ParticipantRow({
  participant: p,
  onDelete,
}: {
  participant: Participant;
  onDelete: (participant: Participant) => Promise<void>;
}) {
  return (
    <motion.li
      className="participants__row"
      layout
      initial={{ opacity: 0, y: -10, backgroundColor: "#fff3c4" }}
      animate={{ opacity: 1, y: 0, backgroundColor: "#ffffff" }}
      transition={{ duration: 0.6 }}
    >
      <div className="participants__top">
        <strong className="participants__phone">{p.phone}</strong>
        <span className="participants__actions">
          <span className={`agent-chip ${p.role === "admin" ? "agent-chip--strategist" : ""}`}>
            {p.invitation_code ?? texts.participants.teamBadge}
          </span>
          <ConfirmButton
            label={texts.participants.remove(p.phone)}
            onConfirm={() => void onDelete(p)}
          >
            <TrashIcon />
          </ConfirmButton>
        </span>
      </div>
      {p.email && <p className="participants__email">{p.email}</p>}
      {!p.verified && (
        <p className="participants__pending" role="status">
          {texts.participants.pending(p.pending_code)}{" "}
          <small>
            {p.code_emailed ? texts.participants.codeEmailed : texts.participants.codeNotEmailed}
          </small>
        </p>
      )}
      <p className="participants__meta">
        {texts.participants.registeredAt(formatDateTime(new Date(p.registered_at)))}
        {" · "}
        {p.last_login_at
          ? texts.participants.lastLogin(formatDateTime(new Date(p.last_login_at)))
          : texts.participants.neverLoggedIn}
      </p>
    </motion.li>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <span className="stat__label">{label}</span>
      <span className="stat__value">{value}</span>
    </div>
  );
}
