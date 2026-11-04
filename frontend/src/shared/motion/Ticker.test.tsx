import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Ticker } from "./Ticker";

describe("Ticker", () => {
  it("se lee como el precio completo y dibuja una columna por dígito", () => {
    const { container } = render(<Ticker value="S/ 1523,76" />);
    expect(screen.getByLabelText("S/ 1523,76")).toBeInTheDocument();
    expect(container.querySelectorAll(".ticker__digit")).toHaveLength(6);
  });
});
