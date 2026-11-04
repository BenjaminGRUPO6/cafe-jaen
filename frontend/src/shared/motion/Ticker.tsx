import { motion } from "framer-motion";

const DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];

/**
 * Muestra un texto (por ejemplo «S/ 1234,50») y hace rodar cada dígito cuando el
 * precio cambia, como en una pizarra de bolsa. Los lectores de pantalla leen el
 * texto completo, no los dígitos sueltos.
 */
export function Ticker({ value, className }: { value: string; className?: string }) {
  return (
    <span className={className} aria-label={value}>
      <span className="ticker" aria-hidden="true">
        {[...value].map((char, index) =>
          DIGITS.includes(char) ? (
            <Digit key={`${value.length}-${index}`} digit={Number(char)} />
          ) : (
            <span key={`${value.length}-${index}`} className="ticker__static">
              {char}
            </span>
          ),
        )}
      </span>
    </span>
  );
}

function Digit({ digit }: { digit: number }) {
  return (
    <span className="ticker__digit">
      <motion.span
        className="ticker__column"
        initial={false}
        animate={{ y: `${-digit}em` }}
        transition={{ type: "spring", stiffness: 140, damping: 22 }}
      >
        {DIGITS.map((d) => (
          <span key={d}>{d}</span>
        ))}
      </motion.span>
    </span>
  );
}
