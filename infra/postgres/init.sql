-- BD central: maneja tenants, módulos, usuarios globales
-- Equivalente a erp_central en Laravel

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Los schemas de cada tenant se crean dinámicamente
-- cuando se registra un hospital nuevo, igual que
-- Stancl Tenancy creaba una BD por tenant