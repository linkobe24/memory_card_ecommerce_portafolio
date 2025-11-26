export interface OrderItem {
  id: string;
  game_id: string;
  game_title: string;
  price: number;
  quantity: number;
}

export interface Order {
  id: string;
  user_id: string;
  items: OrderItem[];
  total: number;
  status: "pending" | "completed" | "cancelled";
  created_at: string;
}
