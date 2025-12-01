// <GameCard.Image />, <GameCard.Title />, etc.
import { GameCard as Root } from "./GameCard";
import { GameCardImage as Image } from "./GameCardImage";
import { GameCardContent as Content } from "./GameCardContent";
import { GameCardTitle as Title } from "./GameCardTitle";
import { GameCardGenre as Genre } from "./GameCardGenre";
import { GameCardRating as Rating } from "./GameCardRating";
import { GameCardFooter as Footer } from "./GameCardFooter";
import { GameCardPrice as Price } from "./GameCardPrice";
import { GameCardAddToCartButton as AddToCartButton } from "./GameCardAddToCartButton";

export const GameCard = Object.assign(Root, {
  Image,
  Content,
  Title,
  Genre,
  Rating,
  Footer,
  Price,
  AddToCartButton,
});

export type { Game } from "./types";
