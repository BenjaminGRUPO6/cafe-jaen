import { motion } from "framer-motion";
import { useId } from "react";

interface Option<T extends string> {
  value: T;
  label: string;
}

/** Control segmentado: la pastilla oscura se desliza hasta la opción elegida. */
export function Segmented<T extends string>({
  options,
  value,
  onChange,
  label,
}: {
  options: Option<T>[];
  value: T;
  onChange: (value: T) => void;
  label: string;
}) {
  // Cada control tiene su propia pastilla (dos controles en pantalla no se mezclan)
  const pillId = useId();
  return (
    <div className="segmented" role="group" aria-label={label}>
      {options.map((option) => {
        const selected = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            className="segmented__option"
            aria-pressed={selected}
            onClick={() => onChange(option.value)}
          >
            {selected && (
              <motion.span
                layoutId={pillId}
                className="segmented__pill"
                transition={{ type: "spring", stiffness: 420, damping: 34 }}
              />
            )}
            <span className="segmented__label">{option.label}</span>
          </button>
        );
      })}
    </div>
  );
}
