import { useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { listen } from "../api/stream";
import type { LivePrice } from "../api/types";
import { texts } from "../texts/es";

interface LivePriceState {
  price: LivePrice | null;
  error: ApiError | null;
}

/** Precio en vivo: se actualiza solo cada vez que la API envía una cotización nueva (HU03). */
export function useLivePrice(): LivePriceState {
  const [state, setState] = useState<LivePriceState>({ price: null, error: null });

  useEffect(
    () =>
      listen(
        "/prices/stream",
        (event) => {
          if (event.event === "price") {
            setState({ price: JSON.parse(event.data) as LivePrice, error: null });
          }
        },
        // Se conserva el último precio recibido; solo se avisa que se perdió la conexión
        () =>
          setState((current) => ({
            ...current,
            error: new ApiError(texts.common.genericError, 0),
          })),
      ),
    [],
  );

  return state;
}
