import { texts } from "../texts/es";

interface Props {
  loading?: boolean;
  error?: { message: string } | null;
  onRetry?: () => void;
}

/** Muestra «Cargando…» o un error con botón para reintentar. */
export function StatusMessage({ loading, error, onRetry }: Props) {
  if (loading) return <p className="status">{texts.common.loading}</p>;
  if (!error) return null;
  return (
    <div className="status status--error" role="alert">
      <p>{error.message}</p>
      {onRetry && (
        <button className="button button--secondary" onClick={onRetry}>
          {texts.common.retry}
        </button>
      )}
    </div>
  );
}
