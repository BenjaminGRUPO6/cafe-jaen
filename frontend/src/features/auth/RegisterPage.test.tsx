import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AuthProvider } from "../../shared/auth/AuthContext";
import { texts } from "../../shared/texts/es";
import { RegisterPage } from "./RegisterPage";

describe("RegisterPage (PA-01-3)", () => {
  it("no permite crear la cuenta sin aceptar el consentimiento", () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <RegisterPage />
        </MemoryRouter>
      </AuthProvider>,
    );
    const submit = screen.getByRole("button", { name: texts.auth.register });

    expect(submit).toBeDisabled();
    fireEvent.click(screen.getByLabelText(texts.auth.consentAccept));
    expect(submit).toBeEnabled();
  });
});
