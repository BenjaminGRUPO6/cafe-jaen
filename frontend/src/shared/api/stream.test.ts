import { describe, expect, it } from "vitest";
import { parseSse } from "./stream";

describe("lectura del flujo en vivo (PA-03-3)", () => {
  it("separa eventos completos e ignora los latidos", () => {
    const text =
      'event: price\ndata: {"price_soles": 1140.89}\n\n: ping\n\nevent: price\ndata: {"pr';

    const { events, rest } = parseSse(text);

    expect(events).toEqual([{ event: "price", data: '{"price_soles": 1140.89}' }]);
    expect(rest).toBe('event: price\ndata: {"pr');
  });

  it("completa un evento que llegó en dos partes", () => {
    const first = parseSse('event: price\ndata: {"a"');
    const second = parseSse(first.rest + ": 1}\n\n");

    expect(second.events).toEqual([{ event: "price", data: '{"a": 1}' }]);
  });
});
