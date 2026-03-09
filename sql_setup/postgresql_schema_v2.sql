-- ============================================================
--  Video Game Sales & Engagement Analysis
--  PostgreSQL Schema — videogame_analytics
--  EXACT column names from cleaned CSVs
-- ============================================================

-- ── Safe drop ──────────────────────────────────────────────
DROP VIEW  IF EXISTS vw_engagement_sales      CASCADE;
DROP VIEW  IF EXISTS vw_developer_stats       CASCADE;
DROP VIEW  IF EXISTS vw_yearly_trends         CASCADE;
DROP VIEW  IF EXISTS vw_publisher_performance CASCADE;
DROP VIEW  IF EXISTS vw_platform_sales        CASCADE;
DROP VIEW  IF EXISTS vw_genre_rating          CASCADE;
DROP TABLE IF EXISTS merged_data              CASCADE;
DROP TABLE IF EXISTS game_sales               CASCADE;
DROP TABLE IF EXISTS game_engagement          CASCADE;
DROP TABLE IF EXISTS dim_publisher            CASCADE;
DROP TABLE IF EXISTS dim_developer            CASCADE;
DROP TABLE IF EXISTS dim_platform             CASCADE;
DROP TABLE IF EXISTS dim_genre                CASCADE;

-- ============================================================
--  DIMENSION TABLES
-- ============================================================

CREATE TABLE dim_genre (
    genre_id   SERIAL       PRIMARY KEY,
    genre_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE dim_platform (
    platform_id   SERIAL       PRIMARY KEY,
    platform_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE dim_developer (
    developer_id   SERIAL       PRIMARY KEY,
    developer_name VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE dim_publisher (
    publisher_id   SERIAL       PRIMARY KEY,
    publisher_name VARCHAR(300) NOT NULL UNIQUE
);

-- ============================================================
--  FACT TABLE 1 — game_engagement
-- ============================================================

CREATE TABLE game_engagement (
    game_id           INTEGER       PRIMARY KEY,
    game_title        VARCHAR(500)  NOT NULL,
    release_date      DATE,
    release_year      SMALLINT,
    release_month     SMALLINT,
    rating            NUMERIC(3,1),
    times_listed      INTEGER,
    num_reviews       INTEGER,
    plays             INTEGER,
    playing           INTEGER,
    backlogs          INTEGER,
    wishlist          INTEGER,
    genres_clean      TEXT,
    primary_genre     VARCHAR(100),
    team_clean        TEXT,
    primary_developer VARCHAR(300),
    -- Foreign Keys
    genre_id          INTEGER REFERENCES dim_genre(genre_id),
    developer_id      INTEGER REFERENCES dim_developer(developer_id)
);

-- ============================================================
--  FACT TABLE 2 — game_sales
-- ============================================================

CREATE TABLE game_sales (
    sales_id     INTEGER       PRIMARY KEY,
    game_title   VARCHAR(500)  NOT NULL,
    platform     VARCHAR(100),
    release_year SMALLINT,
    genre        VARCHAR(100),
    publisher    VARCHAR(300),
    na_sales     NUMERIC(8,2)  DEFAULT 0,
    eu_sales     NUMERIC(8,2)  DEFAULT 0,
    jp_sales     NUMERIC(8,2)  DEFAULT 0,
    other_sales  NUMERIC(8,2)  DEFAULT 0,
    global_sales NUMERIC(8,2)  DEFAULT 0,
    -- Foreign Keys
    platform_id  INTEGER REFERENCES dim_platform(platform_id),
    publisher_id INTEGER REFERENCES dim_publisher(publisher_id),
    genre_id     INTEGER REFERENCES dim_genre(genre_id)
);

-- ============================================================
--  MERGED TABLE
-- ============================================================

CREATE TABLE merged_data (
    merged_id         SERIAL        PRIMARY KEY,
    game_title        VARCHAR(500),
    release_year      SMALLINT,
    rating            NUMERIC(3,1),
    plays             INTEGER,
    backlogs          INTEGER,
    wishlist          INTEGER,
    primary_genre     VARCHAR(100),
    primary_developer VARCHAR(300),
    publisher         VARCHAR(300),
    na_sales          NUMERIC(8,2)  DEFAULT 0,
    eu_sales          NUMERIC(8,2)  DEFAULT 0,
    jp_sales          NUMERIC(8,2)  DEFAULT 0,
    other_sales       NUMERIC(8,2)  DEFAULT 0,
    global_sales      NUMERIC(8,2)  DEFAULT 0,
    sales_genre       VARCHAR(100),
    platforms         TEXT,
    rating_tier       VARCHAR(20),
    sales_tier        VARCHAR(30)
);


select * from game_engagement
select * from game_sales
select * from merged_data
-- ============================================================
--  INDEXES
-- ============================================================

CREATE INDEX idx_eng_genre       ON game_engagement(primary_genre);
CREATE INDEX idx_eng_year        ON game_engagement(release_year);
CREATE INDEX idx_eng_rating      ON game_engagement(rating);
CREATE INDEX idx_eng_developer   ON game_engagement(primary_developer);
CREATE INDEX idx_sales_platform  ON game_sales(platform);
CREATE INDEX idx_sales_genre     ON game_sales(genre);
CREATE INDEX idx_sales_year      ON game_sales(release_year);
CREATE INDEX idx_sales_publisher ON game_sales(publisher);
CREATE INDEX idx_merged_genre    ON merged_data(primary_genre);
CREATE INDEX idx_merged_year     ON merged_data(release_year);
CREATE INDEX idx_merged_sales    ON merged_data(global_sales);

-- ============================================================
--  VIEWS
-- ============================================================

CREATE VIEW vw_genre_rating AS
SELECT
    primary_genre                                   AS genre,
    COUNT(*)                                        AS total_games,
    ROUND(AVG(rating)::NUMERIC, 2)                  AS avg_rating,
    ROUND((SUM(plays)/1000000.0)::NUMERIC, 3)       AS total_plays_M,
    ROUND((SUM(wishlist)/1000.0)::NUMERIC, 2)       AS total_wishlist_K
FROM game_engagement
WHERE primary_genre IS NOT NULL
GROUP BY primary_genre
ORDER BY avg_rating DESC;

CREATE VIEW vw_platform_sales AS
SELECT
    platform,
    COUNT(DISTINCT game_title)                      AS total_games,
    ROUND(SUM(global_sales)::NUMERIC, 2)            AS total_global_sales_M,
    ROUND(SUM(na_sales)::NUMERIC, 2)                AS total_na_sales_M,
    ROUND(SUM(eu_sales)::NUMERIC, 2)                AS total_eu_sales_M,
    ROUND(SUM(jp_sales)::NUMERIC, 2)                AS total_jp_sales_M
FROM game_sales
GROUP BY platform
ORDER BY total_global_sales_M DESC;

CREATE VIEW vw_publisher_performance AS
SELECT
    publisher,
    COUNT(DISTINCT game_title)                      AS total_titles,
    ROUND(SUM(global_sales)::NUMERIC, 2)            AS total_global_sales_M,
    ROUND(AVG(global_sales)::NUMERIC, 3)            AS avg_sales_per_title
FROM game_sales
WHERE publisher != 'Unknown'
GROUP BY publisher
ORDER BY total_global_sales_M DESC;

CREATE VIEW vw_yearly_trends AS
SELECT
    release_year                                    AS year,
    COUNT(DISTINCT game_title)                      AS games_released,
    ROUND(SUM(global_sales)::NUMERIC, 2)            AS total_global_sales_M,
    ROUND(SUM(na_sales)::NUMERIC, 2)                AS na_sales_M,
    ROUND(SUM(eu_sales)::NUMERIC, 2)                AS eu_sales_M,
    ROUND(SUM(jp_sales)::NUMERIC, 2)                AS jp_sales_M
FROM game_sales
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year;

CREATE VIEW vw_engagement_sales AS
SELECT
    game_title,
    rating,
    rating_tier,
    plays,
    wishlist,
    backlogs,
    primary_genre,
    global_sales,
    na_sales,
    eu_sales,
    jp_sales,
    release_year,
    sales_tier
FROM merged_data
ORDER BY global_sales DESC;

CREATE VIEW vw_developer_stats AS
SELECT
    primary_developer                               AS developer,
    COUNT(*)                                        AS total_games,
    ROUND(AVG(rating)::NUMERIC, 2)                  AS avg_rating,
    ROUND((SUM(plays)/1000.0)::NUMERIC, 1)          AS total_plays_K,
    ROUND((SUM(wishlist)/1000.0)::NUMERIC, 1)       AS total_wishlist_K
FROM game_engagement
WHERE primary_developer IS NOT NULL
  AND primary_developer != 'Unknown'
GROUP BY primary_developer
HAVING COUNT(*) >= 2
ORDER BY avg_rating DESC;
