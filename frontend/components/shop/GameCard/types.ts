export interface Game {
  id: string;
  title: string;
  description: string;
  image: string;
  price: number;
  originalPrice?: number; // para descuentos
  genre: string;
  rating: number;
  platform: string[];
  releaseDate: string;
  developer: string;
  inStock: boolean;
  stockCount: number;
}

export interface GameCardContextValue {
  game: Game;
  onAddToCart?: (game: Game) => void;
  onRemove?: (game: Game) => void;
  isInCart?: boolean;
}
