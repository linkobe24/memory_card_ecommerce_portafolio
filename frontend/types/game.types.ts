export interface Game {
  id: string;
  rawg_id: string;
  title: string;
  description: string;
  image_url: string;
  price: number;
  stock: number;
  genre: string;
  platform: string;
  rating: number;
  release_date: string;
  created_at: string;
}

export interface GameFilters {
  search?: string;
  genre?: string;
  platform?: string;
  min_price?: number;
  max_price?: number;
  page?: number;
  limit?: number;
}
