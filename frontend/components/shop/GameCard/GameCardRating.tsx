"use client";

import { Star, StarHalf } from "lucide-react";
import { useGameCard } from "./context";
import { useMemo } from "react";
interface GameCardRatingProps {
  className?: string;
  showNumber?: boolean;
}

export function GameCardRating({
  className = "",
  showNumber = true,
}: GameCardRatingProps) {
  const { game } = useGameCard();
  const rating = Math.min(5, Math.max(0, Number(game.rating) || 0));

  const stars = useMemo(() => {
    const list = [];
    const full = Math.floor(rating);
    const half = rating % 1 >= 0.5 ? 1 : 0;
    const empty = 5 - full - half;

    for (let i = 0; i < full; i++) {
      list.push(<Star key={`full-${i}`} className="w-4 h-4 fill-accent" />);
    }

    if (half) {
      list.push(<StarHalf key="half" className="w-4 h-4 fill-accent" />);
    }

    for (let i = 0; i < empty; i++) {
      list.push(
        <Star key={`empty-${i}`} className="w-4 h-4 fill-neutral-600" />
      );
    }

    return list;
  }, [rating]);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex gap-0.5">{stars}</div>
      {showNumber && (
        <span className="text-sm text-muted-foreground">
          {rating.toFixed(1)}/5
        </span>
      )}
    </div>
  );
}
