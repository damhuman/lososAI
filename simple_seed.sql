-- Simple seed data for seafood store
BEGIN;

-- Categories
INSERT INTO categories (id, name, icon, "order", is_active) VALUES
('salmon', 'Лосось', '🐟', 1, true),
('shellfish', 'Молюски', '🦐', 2, true),
('tomyum', 'Том Ям набори', '🍲', 3, true),
('caviar', 'Ікра', '🥚', 4, true)
ON CONFLICT (id) DO NOTHING;

-- Districts  
INSERT INTO districts (name, is_active, delivery_cost) VALUES
('Центр', true, 0),
('Печерський район', true, 50),
('Оболонь', true, 75),
('Позняки', true, 100),
('Дарниця', true, 100)
ON CONFLICT (name) DO NOTHING;

-- Products
INSERT INTO products (id, category_id, name, description, price_per_kg, packages, is_active, is_featured) VALUES
('salmon_smoked_001', 'salmon', 'Копчений лосось преміум', 'Норвезький лосось холодного копчення', 1200.00, '[{"id": "200g", "weight": 0.2, "unit": "г", "available": true}, {"id": "500g", "weight": 0.5, "unit": "г", "available": true}]', true, true),
('salmon_fresh_001', 'salmon', 'Свіжий лосось філе', 'Свіже філе атлантичного лосося', 800.00, '[{"id": "1kg", "weight": 1, "unit": "кг", "available": true}, {"id": "500g", "weight": 0.5, "unit": "г", "available": true}]', true, false),
('shrimp_king_001', 'shellfish', 'Королівські креветки', 'Великі креветки 16-20 шт/кг', 650.00, '[{"id": "500g", "weight": 0.5, "unit": "г", "available": true}, {"id": "1kg", "weight": 1, "unit": "кг", "available": true}]', true, true),
('mussels_001', 'shellfish', 'Мідії варено-морожені', 'Очищені мідії готові до вживання', 300.00, '[{"id": "500g", "weight": 0.5, "unit": "г", "available": true}]', true, false),
('tomyum_classic_001', 'tomyum', 'Том Ям класичний набір', 'Креветки, гриби, лемонграс, лайм', 450.00, '[{"id": "set", "weight": 0.8, "unit": "набір", "available": true}]', true, true),
('caviar_red_001', 'caviar', 'Червона ікра горбуші', 'Преміум ікра горбуші', 2500.00, '[{"id": "100g", "weight": 0.1, "unit": "г", "available": true}, {"id": "250g", "weight": 0.25, "unit": "г", "available": true}]', true, true)
ON CONFLICT (id) DO NOTHING;

-- Promo codes
INSERT INTO promo_codes (code, discount_percent, is_active, is_gold_code) VALUES
('GOLD2024', 15, true, true),
('NEWBIE10', 10, true, false),
('SEAFOOD20', 20, true, false)
ON CONFLICT (code) DO NOTHING;

COMMIT;