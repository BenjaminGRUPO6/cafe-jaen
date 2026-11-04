import { Link } from "react-router-dom";
import { BeanIcon } from "../motion/icons";
import { texts } from "../texts/es";

/** Logotipo: un grano de café en un círculo dorado y el nombre de la app. */
export function Brand() {
  return (
    <Link to="/" className="brand">
      <span className="brand__mark">
        <BeanIcon />
      </span>
      {texts.appName}
    </Link>
  );
}
