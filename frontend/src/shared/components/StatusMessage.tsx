import { texts } from "../texts/es";

interface Props {
  loading?: boolean;
  error?: { message: string } | null;
  onRetry?: () => void;
}

/** Muestra bloques de carga o un error con botón para reintentar. */
export function StatusMessage({ loading, error, onRetry }: Props) {
  if (loading) {
    return (
      <div className="skeleton" role="status" aria-label={texts.common.loading}>
        <span className="skeleton__block" />
        <span className="skeleton__block skeleton__block--short" />
      </div>
    );
  }
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
