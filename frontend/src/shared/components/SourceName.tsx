import { quoteSourceUrl } from "../sources";

/** Nombre de una web de la bolsa como enlace a su página (abre en otra pestaña). */
export function SourceName({ name }: { name: string }) {
  const url = quoteSourceUrl(name);
  if (!url) return <>{name}</>;
  return (
    <a className="source-name" href={url} target="_blank" rel="noopener noreferrer">
      {name}
    </a>
  );
}

/** Varias fuentes separadas por comas, cada una con su enlace. */
export function SourceNames({ names }: { names: string[] }) {
  return (
    <>
      {names.map((name, index) => (
        <span key={name}>
          {index > 0 && ", "}
          <SourceName name={name} />
        </span>
      ))}
    </>
  );
}
