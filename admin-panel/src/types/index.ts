export interface Category {
  id: string;
  name: string;
  description?: string;
  icon: string;
  order: number;
  is_active: boolean;
}

export interface PackageInfo {
  id: string;
  weight: number;
  unit: string;
  available: boolean;
  note?: string;
}

export interface ProductPackage {
  id: number;
  product_id: string;
  package_id: string;
  name: string;
  weight: number;
  unit: string;
  price: number;
  image_url?: string;
  available: boolean;
  sort_order: number;
  note?: string;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  category_id: string;
  name: string;
  description?: string;
  price_per_kg: number;
  image_url?: string;
  packages: PackageInfo[]; // Legacy field
  product_packages?: ProductPackage[]; // New relational packages
  is_active: boolean;
  is_featured: boolean;
  stock_quantity?: number;
  category: Category;
}

export interface User {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code: string;
  is_bot: boolean;
  is_premium: boolean;
  is_gold_client: boolean;
  is_blocked: boolean;
  created_at: string;
}

export interface District {
  id: number;
  name: string;
  is_active: boolean;
  delivery_cost: number;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: string;
  product_name: string;
  package_id: string;
  weight: number;
  unit: string;
  quantity: number;
  price_per_unit: number;
  total_price: number;
}

export interface Order {
  id: number;
  user_id: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'delivering' | 'delivered' | 'cancelled';
  total_amount: number;
  promo_code_used?: string;
  discount_amount: number;
  district_id: number;
  delivery_time_slot: 'morning' | 'afternoon' | 'evening';
  delivery_date: string;
  delivery_address?: string;
  comment?: string;
  contact_name: string;
  contact_phone?: string;
  created_at: string;
  updated_at?: string;
  items: OrderItem[];
  user: User;
  district: District;
}

export interface PromoCode {
  id: number;
  code: string;
  discount_percent: number;
  discount_amount: number;
  is_active: boolean;
  usage_limit?: number;
  usage_count: number;
  is_gold_code: boolean;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends AuthTokens {
  admin: AdminUser;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}