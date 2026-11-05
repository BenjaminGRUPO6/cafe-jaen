import { AnimatePresence, motion } from "framer-motion";
import { useId, useState, type ReactNode } from "react";
import { InfoIcon } from "../motion/icons";
import { texts } from "../texts/es";

/** Botón «¿Cómo se calcula?» que despliega una nota con la fórmula y los números del momento. */
export function InfoNote({
  children,
  label = texts.info.howCalculated,
}: {
  children: ReactNode;
  label?: string;
}) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className="info-note">
      <button
        type="button"
        className="info-note__toggle"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen((value) => !value)}
      >
        <InfoIcon />
        {open ? texts.info.close : label}
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={id}
            className="info-note__body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <div className="info-note__content">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
