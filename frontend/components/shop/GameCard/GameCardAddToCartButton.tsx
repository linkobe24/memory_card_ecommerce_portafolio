"use client";

import { Button } from "@/components/ui";
import { useGameCard } from "./context";
import { Check, ShoppingCart } from "lucide-react";

interface GameCardAddToCartButtonProps {
  className?: string;
}

export function GameCardAddToCartButton({
  className = "",
}: GameCardAddToCartButtonProps) {
  const { game, onAddToCart, onRemove, isInCart } = useGameCard();

  const handleClick = () => {
    if (isInCart && onRemove) {
      onRemove(game);
    } else if (onAddToCart && !isInCart) {
      onAddToCart(game);
    }
  };

  if (!game.inStock) {
    return (
      <Button disabled variant="outline" className={className}>
        Sin Stock
      </Button>
    );
  }

  return (
    <Button
      onClick={handleClick}
      variant="outline"
      className={`gap-2 min-w-40 border-2 ${
        isInCart
          ? "bg-green-500/10 border-green-500 text-green-600 hover:bg-green-500/20 dark:bg-green-500/20 dark:border-green-400 dark:text-green-400"
          : "border-primary hover:bg-primary/10"
      } ${className}`}
    >
      {isInCart ? (
        <>
          <Check className="w-4 h-4" />
          En el carrito
        </>
      ) : (
        <>
          <ShoppingCart className="w-4 h-4" />
          Agregar a carrito
        </>
      )}
    </Button>
  );
}
