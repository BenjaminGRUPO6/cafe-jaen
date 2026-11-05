import { REFERENCE_SOURCES, isDemoSource, quoteSourceLinks } from "../sources";
import { ExternalIcon } from "../motion/icons";
import { texts } from "../texts/es";

/** Botones que abren la página de donde sale cada dato (en otra pestaña). */
export function SourceLinks({ sources }: { sources: string[] }) {
  const links = [...quoteSourceLinks(sources), ...REFERENCE_SOURCES];
  return (
    <section className="sources" aria-labelledby="sources-title">
      <h2 id="sources-title" className="sources__title">
        {texts.sources.title}
      </h2>
      {isDemoSource(sources) && <p className="muted">{texts.sources.demo}</p>}
      <ul className="sources__list">
        {links.map((link) => (
          <li key={link.name}>
            <a className="source-link" href={link.url} target="_blank" rel="noopener noreferrer">
              <span>
                <strong>{link.name}</strong>
                <small>{link.detail}</small>
              </span>
              <ExternalIcon />
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
