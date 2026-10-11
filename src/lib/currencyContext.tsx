"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { defaultCurrency, type Currency } from "@/content/membership.config";

interface CurrencyContextValue {
  currency: Currency;
  setCurrency: (currency: Currency) => void;
}

const CurrencyContext = createContext<CurrencyContextValue | null>(null);

/**
 * Shares one GBP/USD selection between the Membership and Add Credits
 * sections (which live in different columns of the homepage) so switching
 * currency in one place updates both, instead of each section keeping its
 * own toggle.
 */
export function CurrencyProvider({ children }: { children: ReactNode }) {
  const [currency, setCurrency] = useState<Currency>(defaultCurrency);
  return (
    <CurrencyContext.Provider value={{ currency, setCurrency }}>
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrency(): CurrencyContextValue {
  const ctx = useContext(CurrencyContext);
  if (!ctx) throw new Error("useCurrency must be used within a CurrencyProvider");
  return ctx;
}
