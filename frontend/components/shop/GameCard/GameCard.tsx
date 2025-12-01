"use client";

import { ReactNode } from "react";
import { Game } from "./types";
import { GameCardContext } from "./context";
import { Card } from "@/components/ui";

interface GameCardProps {
  game: Game;
  onAddToCart?: (game: Game) => void;
  onRemove?: (game: Game) => void;
  isInCart?: boolean;
  children: ReactNode;
  className?: string;
}

/**
 * Componente root del GameCard
 *
 * @example
 * <GameCard game={game} onAddToCart={handleAdd}>
 *   <GameCard.Image />
 *   <GameCard.Content>
 *     <GameCard.Title />
 *     <GameCard.Price />
 *   </GameCard.Content>
 *   <GameCard.AddToCartButton />
 * </GameCard>
 */

export function GameCard({
  game,
  onAddToCart,
  onRemove,
  isInCart = false,
  children,
  className = "",
}: GameCardProps) {
  return (
    <GameCardContext.Provider value={{ game, onAddToCart, onRemove, isInCart }}>
      <Card
        className={`overflow-hidden transition-smooth hover:glow-primary py-0 pb-3 gap-3 ${className}`}
      >
        {children}
      </Card>
    </GameCardContext.Provider>
  );
}
