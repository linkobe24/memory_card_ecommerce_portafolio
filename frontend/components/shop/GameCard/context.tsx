"use client";

import { createContext, useContext } from "react";
import { type GameCardContextValue } from "./types";

const GameCardContext = createContext<GameCardContextValue | null>(null);

function useGameCard() {
  const context = useContext(GameCardContext);

  if (!context) {
    throw new Error("GameCard debe estar dentro del contexto");
  }

  return context;
}

export { GameCardContext, useGameCard };
