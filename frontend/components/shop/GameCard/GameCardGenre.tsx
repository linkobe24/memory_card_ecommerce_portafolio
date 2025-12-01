"use client";

import { Badge } from "@/components/ui";
import { useGameCard } from "./context";

interface GameCardGenreProps {
  className?: string;
}

export function GameCardGenre({ className = "" }: GameCardGenreProps) {
  const { game } = useGameCard();

  return (
    <Badge variant="outline" className={className}>
      {game.genre}
    </Badge>
  );
}
