export interface CartItem {
  id: string;
  game_id: string;
  game: {
    id: string;
    title: string;
    image_url: string;
    price: number;
  };
  quantity: number;
}

export interface Cart {
  id: string;
  uder_id: string;
  items: CartItem[];
  total: number;
  created_at: string;
  updated_at: string;
}
