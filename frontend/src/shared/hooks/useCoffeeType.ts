import { useState } from "react";
import type { CoffeeType } from "../api/types";
import { readStored, writeStored } from "../storage";

const KEY = "cafe-jaen.coffee-type";

/** Tipo de café elegido por el caficultor; se recuerda entre pantallas y visitas (HU12). */
export function useCoffeeType(): [CoffeeType, (type: CoffeeType) => void] {
  const [chosen, setChosen] = useState<CoffeeType>(
    () => (readStored(KEY) as CoffeeType | null) ?? "convencional",
  );
  const choose = (type: CoffeeType) => {
    setChosen(type);
    writeStored(KEY, type);
  };
  return [chosen, choose];
}
