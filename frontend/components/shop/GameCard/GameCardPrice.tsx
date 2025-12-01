"use client";

import { useGameCard } from "./context";

interface GameCardPriceProps {
  className?: string;
  showOriginal?: boolean;
}

export function GameCardPrice({
  className = "",
  showOriginal = true,
}: GameCardPriceProps) {
  const { game } = useGameCard();

  const hasDicount = game.originalPrice && game.originalPrice > game.price;
  const discountPercent = hasDicount
    ? Math.round(
        ((game.originalPrice! - game.price) / game.originalPrice!) * 100
      )
    : 0;

  return (
    <div className={`flex flex-col ${className}`}>
      {hasDicount && showOriginal && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground line-through">
            ${game.originalPrice?.toFixed(2)}
          </span>
          <span className="text-xs font-bold text-accent">
            -{discountPercent}%
          </span>
        </div>
      )}
      <span className="text-2xl font-bold text-primary">
        ${game.price.toFixed(2)}
      </span>
    </div>
  );
}
