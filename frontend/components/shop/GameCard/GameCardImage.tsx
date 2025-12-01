"use client";

import Image from "next/image";
import { useGameCard } from "./context";
import { Badge } from "@/components/ui";

interface GameCardImageProps {
  className?: string;
  showBadges?: boolean;
  showGenre?: boolean;
}

/**
 * Retorna las clases de color según el género del juego
 */
function getGenreColor(genre: string): string {
  const genreColors: Record<string, string> = {
    RPG: "bg-purple-500 text-white",
    Action: "bg-red-500 text-white",
    Adventure: "bg-green-500 text-white",
    Strategy: "bg-blue-500 text-white",
    Shooter: "bg-orange-500 text-white",
    Sports: "bg-yellow-500 text-white",
    Racing: "bg-pink-500 text-white",
    Simulation: "bg-teal-500 text-white",
    Puzzle: "bg-indigo-500 text-white",
    Horror: "bg-gray-800 text-white",
  };

  return genreColors[genre] || "bg-gray-500 text-white";
}

/**
 * Muestra la imagen del juego
 * Opcionalmente muestra badges de "New", "On Sale", "Out of Stock"
 * Opcionalmente muestra el género sobre la imagen
 */
export function GameCardImage({
  className = "",
  showBadges = true,
  showGenre = false,
}: GameCardImageProps) {
  const { game } = useGameCard();

  // calcular nuevo lanzamiento (30 dias)
  const isNew = () => {
    const release = new Date(game.releaseDate).getTime();
    const now = Date.now();
    const thirtyDays = 30 * 24 * 60 * 60 * 1000;

    return now - release <= thirtyDays;
  };

  const hasDiscount = game.originalPrice && game.originalPrice > game.price;

  return (
    <div className={`relative aspect-video overflow-hidden ${className}`}>
      <Image
        src={game.image}
        alt={game.title}
        fill
        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
        className="object-cover transition-smooth hover:scale-105"
        priority={false}
      />

      {/* Badges superiores derecha */}
      {showBadges && (
        <div className="absolute top-2 right-2 flex flex-col gap-1.5">
          {isNew() && (
            <Badge variant="default" className="shadow-md">
              New
            </Badge>
          )}
          {hasDiscount && (
            <Badge className="bg-red-500 text-white border-transparent shadow-md">
              Sale
            </Badge>
          )}
          {!game.inStock && (
            <Badge variant="secondary" className="shadow-md">
              Out of Stock
            </Badge>
          )}
        </div>
      )}

      {/* Badge de género inferior izquierda */}
      {showGenre && (
        <div className="absolute bottom-2 left-2">
          <Badge
            className={`shadow-md border-transparent ${getGenreColor(game.genre)}`}
          >
            {game.genre}
          </Badge>
        </div>
      )}
    </div>
  );
}
