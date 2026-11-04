import { AnimatePresence, motion } from "framer-motion";
import type { ReactNode } from "react";
import { useLocation } from "react-router-dom";

/** Al cambiar de pantalla, la nueva aparece con un fundido corto (responde al toque). */
export function PageTransition({ children }: { children: ReactNode }) {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.16, ease: "easeOut" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
