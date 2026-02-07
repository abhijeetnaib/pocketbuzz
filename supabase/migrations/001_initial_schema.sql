-- PocketBuzz Database Schema
-- Run this in Supabase SQL Editor

-- ===========================================
-- TABLE: restaurants
-- Restaurant profiles and configuration
-- ===========================================
CREATE TABLE IF NOT EXISTS restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    owner_phone TEXT NOT NULL,
    whatsapp_phone_id TEXT,
    inbound_email_address TEXT UNIQUE,
    magic_link_token TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for magic link lookups
CREATE INDEX IF NOT EXISTS idx_restaurants_magic_token ON restaurants(magic_link_token);

-- ===========================================
-- TABLE: universal_records
-- The Data Lake - all customer visit records
-- ===========================================
CREATE TABLE IF NOT EXISTS universal_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    client_phone TEXT NOT NULL,
    client_name TEXT,
    source TEXT DEFAULT 'Dine-In',
    item_ordered TEXT,
    bill_amount NUMERIC(10,2),
    visit_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Critical indexes for performance
CREATE INDEX IF NOT EXISTS idx_records_restaurant ON universal_records(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_records_phone ON universal_records(client_phone);
CREATE INDEX IF NOT EXISTS idx_records_visit ON universal_records(visit_date);
CREATE INDEX IF NOT EXISTS idx_records_source ON universal_records(source);

-- ===========================================
-- ENUMS for campaign types
-- ===========================================
DO $$ BEGIN
    CREATE TYPE strategy_type AS ENUM ('BEST_SELLER', 'DEAD_STOCK', 'CHURN_RECOVERY', 'SLOW_DAY');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE campaign_status AS ENUM ('PENDING', 'APPROVED', 'SENT', 'FAILED');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ===========================================
-- TABLE: campaign_suggestions
-- AI-generated campaign proposals
-- ===========================================
CREATE TABLE IF NOT EXISTS campaign_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    strategy_type strategy_type NOT NULL,
    insight_text TEXT,
    target_audience JSONB DEFAULT '{}',
    generated_image_url TEXT,
    generated_caption TEXT,
    status campaign_status DEFAULT 'PENDING',
    approved_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for campaign lookups
CREATE INDEX IF NOT EXISTS idx_campaigns_restaurant ON campaign_suggestions(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaign_suggestions(status);

-- ===========================================
-- ROW LEVEL SECURITY (RLS)
-- ===========================================
ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
ALTER TABLE universal_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_suggestions ENABLE ROW LEVEL SECURITY;

-- Service role can do everything (for backend)
CREATE POLICY "Service role full access" ON restaurants
    FOR ALL USING (true);
CREATE POLICY "Service role full access" ON universal_records
    FOR ALL USING (true);
CREATE POLICY "Service role full access" ON campaign_suggestions
    FOR ALL USING (true);

-- ===========================================
-- FUNCTIONS for analytics
-- ===========================================

-- Get bestseller item
CREATE OR REPLACE FUNCTION get_bestseller(p_restaurant_id UUID, p_days INT DEFAULT 7)
RETURNS TABLE(item_ordered TEXT, order_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT ur.item_ordered, COUNT(*) as order_count
    FROM universal_records ur
    WHERE ur.restaurant_id = p_restaurant_id
      AND ur.visit_date > (CURRENT_DATE - p_days)
      AND ur.source = 'Dine-In'
      AND ur.item_ordered IS NOT NULL
    GROUP BY ur.item_ordered
    ORDER BY order_count DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Get slowest day of the week
CREATE OR REPLACE FUNCTION get_slowest_day(p_restaurant_id UUID, p_weeks INT DEFAULT 4)
RETURNS TABLE(day_name TEXT, avg_orders NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TO_CHAR(ur.visit_date, 'Day') as day_name,
        COUNT(*)::NUMERIC / p_weeks as avg_orders
    FROM universal_records ur
    WHERE ur.restaurant_id = p_restaurant_id
      AND ur.visit_date > (CURRENT_DATE - (p_weeks * 7))
      AND ur.source = 'Dine-In'
    GROUP BY TO_CHAR(ur.visit_date, 'Day'), EXTRACT(DOW FROM ur.visit_date)
    ORDER BY avg_orders ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Get churning customers (no visit in N days)
CREATE OR REPLACE FUNCTION get_churning_customers(p_restaurant_id UUID, p_inactive_days INT DEFAULT 30)
RETURNS TABLE(client_phone TEXT, last_visit DATE) AS $$
BEGIN
    RETURN QUERY
    SELECT ur.client_phone, MAX(ur.visit_date) as last_visit
    FROM universal_records ur
    WHERE ur.restaurant_id = p_restaurant_id
      AND ur.source = 'Dine-In'
    GROUP BY ur.client_phone
    HAVING MAX(ur.visit_date) < (CURRENT_DATE - p_inactive_days)
       AND COUNT(*) >= 2  -- Was a repeat customer
    ORDER BY last_visit DESC;
END;
$$ LANGUAGE plpgsql;

-- Get weekly stats
CREATE OR REPLACE FUNCTION get_weekly_stats(p_restaurant_id UUID)
RETURNS TABLE(
    new_customers BIGINT,
    total_orders BIGINT,
    total_revenue NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT ur.client_phone) as new_customers,
        COUNT(*) as total_orders,
        COALESCE(SUM(ur.bill_amount), 0) as total_revenue
    FROM universal_records ur
    WHERE ur.restaurant_id = p_restaurant_id
      AND ur.visit_date > (CURRENT_DATE - 7)
      AND ur.source = 'Dine-In';
END;
$$ LANGUAGE plpgsql;

-- Count unique customers
CREATE OR REPLACE FUNCTION count_unique_customers(
    p_restaurant_id UUID,
    p_days INT DEFAULT 30,
    p_source TEXT DEFAULT 'Dine-In'
)
RETURNS BIGINT AS $$
DECLARE
    result BIGINT;
BEGIN
    SELECT COUNT(DISTINCT client_phone) INTO result
    FROM universal_records
    WHERE restaurant_id = p_restaurant_id
      AND visit_date > (CURRENT_DATE - p_days)
      AND source = p_source;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
