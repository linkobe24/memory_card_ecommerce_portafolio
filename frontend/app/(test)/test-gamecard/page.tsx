"use client";

import { Game, GameCard } from "@/components/shop/GameCard";
import { useState } from "react";

const mockGame: Game = {
  id: "1",
  title: "Cyberpunk 2077: Phantom Liberty",
  description: "Phantom Liberty is a spy-thriller expansion for Cyberpunk 2077",
  image:
    "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&h=450&fit=crop",
  price: 29.99,
  originalPrice: 49.99,
  genre: "RPG",
  rating: 4.5,
  platform: ["PC", "PlayStation", "Xbox"],
  releaseDate: "2023-09-26",
  developer: "CD Projekt Red",
  inStock: true,
  stockCount: 150,
};

export default function TestGameCardPage() {
  const [isInCart, setIsInCart] = useState(false);

  const handleAddToCart = (game: Game) => {
    console.log("Adding to cart:", game.title);
    setIsInCart(true);
  };

  const handleRemoveFromCart = (game: Game) => {
    console.log("Removing from cart:", game.title);
    setIsInCart(false);
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">GameCard Component Test</h1>

      <div className="max-w-sm">
        <GameCard
          game={mockGame}
          onAddToCart={handleAddToCart}
          onRemove={handleRemoveFromCart}
          isInCart={isInCart}
        >
          <GameCard.Image showBadges showGenre />
          <GameCard.Content>
            <GameCard.Title maxLines={2} />
            <GameCard.Rating showNumber />
          </GameCard.Content>
          <GameCard.Footer>
            <GameCard.Price showOriginal />
            <GameCard.AddToCartButton />
          </GameCard.Footer>
        </GameCard>
      </div>
    </div>
  );
}
