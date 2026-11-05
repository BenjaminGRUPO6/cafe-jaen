import { Link } from "react-router-dom";
import { texts } from "../texts/es";

/** Logotipo de Café Jaén (kit visual): el grano con hojas sobre el círculo dorado. */
export function Brand() {
  return (
    <Link to="/" className="brand">
      <img className="brand__logo" src="/logos/cafe-jaen-marca.svg" alt="" width={36} height={36} />
      {texts.appName}
    </Link>
  );
}
