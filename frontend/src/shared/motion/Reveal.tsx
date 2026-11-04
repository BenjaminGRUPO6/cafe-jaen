import { motion, type Variants } from "framer-motion";
import type { ReactNode } from "react";

// Entrada escalonada de los bloques: el único momento coreografiado de la app (al abrirla)
const container: Variants = {
  hidden: {},
  shown: { transition: { staggerChildren: 0.07 } },
};
const item: Variants = {
  hidden: { opacity: 0, y: 18, scale: 0.98 },
  shown: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: "spring", stiffness: 260, damping: 24 },
  },
};

export function RevealGroup({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div className={className} variants={container} initial="hidden" animate="shown">
      {children}
    </motion.div>
  );
}

export function RevealItem({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div className={className} variants={item}>
      {children}
    </motion.div>
  );
}
