"use client";

import { CardTitle } from "@/components/ui";
import { useGameCard } from "./context";

interface GameCardTitleProps {
  className?: string;
  maxLines?: number;
}

export function GameCardTitle({
  className = "",
  maxLines = 2,
}: GameCardTitleProps) {
  const { game } = useGameCard();

  return (
    <CardTitle
      className={`text-lg font-bold leading-tight line-clamp-${maxLines} ${className}`}
    >
      {game.title}
    </CardTitle>
  );
}
