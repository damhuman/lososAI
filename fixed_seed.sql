-- Fixed seed data with proper package structure
BEGIN;

-- First clear existing data
DELETE FROM products;

-- Insert products with correct package structure
INSERT INTO products (id, category_id, name, description, price_per_kg, packages, is_active, is_featured) VALUES
('salmon_smoked_001', 'salmon', 'Копчений лосось преміум', 'Норвезький лосось холодного копчення', 1200.00, 
'[{"id": "200g", "weight": 0.2, "unit": "г", "available": true, "type": "200г", "price": 240}, 
  {"id": "500g", "weight": 0.5, "unit": "г", "available": true, "type": "500г", "price": 600}]', 
true, true),

('salmon_fresh_001', 'salmon', 'Свіжий лосось філе', 'Свіже філе атлантичного лосося', 800.00, 
'[{"id": "500g", "weight": 0.5, "unit": "г", "available": true, "type": "500г", "price": 400}, 
  {"id": "1kg", "weight": 1, "unit": "кг", "available": true, "type": "1кг", "price": 800}]', 
true, false),

('shrimp_king_001', 'shellfish', 'Королівські креветки', 'Великі креветки 16-20 шт/кг', 650.00, 
'[{"id": "500g", "weight": 0.5, "unit": "г", "available": true, "type": "500г", "price": 325}, 
  {"id": "1kg", "weight": 1, "unit": "кг", "available": true, "type": "1кг", "price": 650}]', 
true, true),

('mussels_001', 'shellfish', 'Мідії варено-морожені', 'Очищені мідії готові до вживання', 300.00, 
'[{"id": "500g", "weight": 0.5, "unit": "г", "available": true, "type": "500г", "price": 150}]', 
true, false),

('tomyum_classic_001', 'tomyum', 'Том Ям класичний набір', 'Креветки, гриби, лемонграс, лайм', 450.00, 
'[{"id": "set", "weight": 0.8, "unit": "набір", "available": true, "type": "набір", "price": 360}]', 
true, true),

('caviar_red_001', 'caviar', 'Червона ікра горбуші', 'Преміум ікра горбуші', 2500.00, 
'[{"id": "100g", "weight": 0.1, "unit": "г", "available": true, "type": "100г", "price": 250}, 
  {"id": "250g", "weight": 0.25, "unit": "г", "available": true, "type": "250г", "price": 625}]', 
true, true);

COMMIT;