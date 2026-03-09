-- ============================================================
--  🎮 Video Game Sales & Engagement Analysis
--  EDA — SQL Queries (pgAdmin4 mein run karo)
--  Database: videogame_analytics
-- ============================================================


-- ============================================================
--  SECTION 1 — RATING ANALYSIS
-- ============================================================

-- 1.1 Basic Rating Stats
SELECT
    COUNT(*)                              AS total_games,
    ROUND(AVG(rating)::NUMERIC, 2)        AS avg_rating,
    ROUND(MIN(rating)::NUMERIC, 2)        AS min_rating,
    ROUND(MAX(rating)::NUMERIC, 2)        AS max_rating,
    ROUND(STDDEV(rating)::NUMERIC, 2)     AS std_dev,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY rating) AS q1,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY rating) AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY rating) AS q3
FROM game_engagement;


-- 1.2 Rating Tier Distribution
SELECT
    CASE
        WHEN rating >= 4.0 THEN 'High (4+)'
        WHEN rating >= 3.0 THEN 'Medium (3-4)'
        ELSE 'Low (<3)'
    END                                   AS rating_tier,
    COUNT(*)                              AS total_games,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM game_engagement
WHERE rating IS NOT NULL
GROUP BY rating_tier
ORDER BY MIN(rating) DESC;


-- 1.3 Rating Distribution (Histogram buckets)
SELECT
    ROUND(rating::NUMERIC, 1)             AS rating_bucket,
    COUNT(*)                              AS game_count,
    REPEAT('█', COUNT(*)::INT / 5)        AS bar_chart
FROM game_engagement
WHERE rating IS NOT NULL
GROUP BY ROUND(rating::NUMERIC, 1)
ORDER BY rating_bucket;


-- ============================================================
--  SECTION 2 — SALES ANALYSIS
-- ============================================================

-- 2.1 Global Sales Summary
SELECT
    COUNT(*)                                          AS total_records,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_global_sales_M,
    ROUND(AVG(global_sales)::NUMERIC, 3)              AS avg_sales_M,
    ROUND(MAX(global_sales)::NUMERIC, 2)              AS max_sales_M,
    ROUND(MIN(global_sales)::NUMERIC, 2)              AS min_sales_M,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP
          (ORDER BY global_sales)::NUMERIC, 3)        AS median_sales_M,
    ROUND(SUM(na_sales)::NUMERIC, 2)                  AS total_na_M,
    ROUND(SUM(eu_sales)::NUMERIC, 2)                  AS total_eu_M,
    ROUND(SUM(jp_sales)::NUMERIC, 2)                  AS total_jp_M
FROM game_sales;


-- 2.2 Sales Tier Distribution
SELECT
    CASE
        WHEN global_sales >= 5  THEN 'Blockbuster (5M+)'
        WHEN global_sales >= 1  THEN 'Hit (1-5M)'
        WHEN global_sales > 0   THEN 'Mid-Tier (<1M)'
        ELSE 'No Sales Data'
    END                                               AS sales_tier,
    COUNT(*)                                          AS total_games,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_sales_M,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_games
FROM game_sales
GROUP BY sales_tier
ORDER BY MIN(global_sales) DESC NULLS LAST;


-- 2.3 Regional Market Share
SELECT
    ROUND(SUM(na_sales) * 100.0 / SUM(global_sales), 2)    AS na_share_pct,
    ROUND(SUM(eu_sales) * 100.0 / SUM(global_sales), 2)    AS eu_share_pct,
    ROUND(SUM(jp_sales) * 100.0 / SUM(global_sales), 2)    AS jp_share_pct,
    ROUND(SUM(other_sales) * 100.0 / SUM(global_sales), 2) AS other_share_pct
FROM game_sales;


-- ============================================================
--  SECTION 3 — GENRE ANALYSIS
-- ============================================================

-- 3.1 Genre Overview (Engagement)
SELECT
    primary_genre,
    COUNT(*)                                          AS total_games,
    ROUND(AVG(rating)::NUMERIC, 2)                    AS avg_rating,
    ROUND(MAX(rating)::NUMERIC, 2)                    AS max_rating,
    ROUND((SUM(plays)/1000.0)::NUMERIC, 1)            AS total_plays_K,
    ROUND((AVG(plays))::NUMERIC, 0)                   AS avg_plays,
    ROUND((SUM(wishlist)/1000.0)::NUMERIC, 1)         AS total_wishlist_K,
    ROUND((SUM(backlogs)/1000.0)::NUMERIC, 1)         AS total_backlogs_K
FROM game_engagement
WHERE primary_genre IS NOT NULL
GROUP BY primary_genre
ORDER BY total_games DESC;


-- 3.2 Genre Sales Performance
SELECT
    genre,
    COUNT(DISTINCT game_title)                        AS total_titles,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_sales_M,
    ROUND(AVG(global_sales)::NUMERIC, 3)              AS avg_sales_M,
    ROUND(MAX(global_sales)::NUMERIC, 2)              AS max_sales_M,
    ROUND(SUM(na_sales)::NUMERIC, 2)                  AS na_sales_M,
    ROUND(SUM(eu_sales)::NUMERIC, 2)                  AS eu_sales_M,
    ROUND(SUM(jp_sales)::NUMERIC, 2)                  AS jp_sales_M
FROM game_sales
WHERE genre IS NOT NULL
GROUP BY genre
ORDER BY total_sales_M DESC;


-- 3.3 Genre Market Share (Sales %)
SELECT
    genre,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_sales_M,
    ROUND(SUM(global_sales) * 100.0 /
          SUM(SUM(global_sales)) OVER (), 2)          AS market_share_pct
FROM game_sales
WHERE genre IS NOT NULL
GROUP BY genre
ORDER BY total_sales_M DESC
LIMIT 15;


-- ============================================================
--  SECTION 4 — PLATFORM ANALYSIS
-- ============================================================

-- 4.1 Platform Sales Breakdown
SELECT
    platform,
    COUNT(DISTINCT game_title)                        AS total_games,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_global_M,
    ROUND(SUM(na_sales)::NUMERIC, 2)                  AS na_M,
    ROUND(SUM(eu_sales)::NUMERIC, 2)                  AS eu_M,
    ROUND(SUM(jp_sales)::NUMERIC, 2)                  AS jp_M,
    ROUND(AVG(global_sales)::NUMERIC, 3)              AS avg_sales_per_title,
    ROUND(SUM(na_sales) * 100.0 /
          NULLIF(SUM(global_sales), 0), 1)            AS na_dominance_pct
FROM game_sales
GROUP BY platform
ORDER BY total_global_M DESC
LIMIT 15;


-- 4.2 Platform Market Share
SELECT
    platform,
    ROUND(SUM(global_sales) * 100.0 /
          SUM(SUM(global_sales)) OVER (), 2)          AS market_share_pct,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_sales_M
FROM game_sales
GROUP BY platform
ORDER BY total_sales_M DESC
LIMIT 10;


-- ============================================================
--  SECTION 5 — PUBLISHER ANALYSIS
-- ============================================================

-- 5.1 Top 20 Publishers by Sales
SELECT
    publisher,
    COUNT(DISTINCT game_title)                        AS total_titles,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_global_M,
    ROUND(AVG(global_sales)::NUMERIC, 3)              AS avg_per_title_M,
    ROUND(SUM(na_sales)::NUMERIC, 2)                  AS na_M,
    ROUND(SUM(eu_sales)::NUMERIC, 2)                  AS eu_M,
    ROUND(SUM(jp_sales)::NUMERIC, 2)                  AS jp_M,
    ROUND(MAX(global_sales)::NUMERIC, 2)              AS best_selling_M
FROM game_sales
WHERE publisher != 'Unknown'
GROUP BY publisher
ORDER BY total_global_M DESC
LIMIT 20;


-- 5.2 Publisher Efficiency (Sales per Title)
SELECT
    publisher,
    COUNT(DISTINCT game_title)                        AS total_titles,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_sales_M,
    ROUND(AVG(global_sales)::NUMERIC, 3)              AS avg_sales_per_title
FROM game_sales
WHERE publisher != 'Unknown'
GROUP BY publisher
HAVING COUNT(DISTINCT game_title) >= 10
ORDER BY avg_sales_per_title DESC
LIMIT 15;


-- ============================================================
--  SECTION 6 — YEARLY TRENDS
-- ============================================================

-- 6.1 Year-wise Industry Overview
SELECT
    release_year                                      AS year,
    COUNT(DISTINCT game_title)                        AS games_released,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_sales_M,
    ROUND(AVG(global_sales)::NUMERIC, 3)              AS avg_sales_M,
    ROUND(SUM(na_sales)::NUMERIC, 2)                  AS na_M,
    ROUND(SUM(eu_sales)::NUMERIC, 2)                  AS eu_M,
    ROUND(SUM(jp_sales)::NUMERIC, 2)                  AS jp_M,
    ROUND(SUM(global_sales) /
          NULLIF(COUNT(DISTINCT game_title), 0)::NUMERIC, 3) AS sales_per_game
FROM game_sales
WHERE release_year BETWEEN 1990 AND 2016
GROUP BY release_year
ORDER BY release_year;


-- 6.2 Year-over-Year Sales Growth
WITH yearly AS (
    SELECT
        release_year,
        SUM(global_sales) AS total_sales
    FROM game_sales
    WHERE release_year BETWEEN 1995 AND 2016
    GROUP BY release_year
)
SELECT
    release_year,
    ROUND(total_sales::NUMERIC, 2)                    AS total_sales_M,
    ROUND(total_sales - LAG(total_sales) OVER
          (ORDER BY release_year)::NUMERIC, 2)        AS yoy_change_M,
    ROUND((total_sales - LAG(total_sales) OVER
           (ORDER BY release_year)) * 100.0 /
           NULLIF(LAG(total_sales) OVER
           (ORDER BY release_year), 0)::NUMERIC, 1)   AS yoy_growth_pct
FROM yearly
ORDER BY release_year;


-- 6.3 Genre Popularity Over Decades
SELECT
    CASE
        WHEN release_year BETWEEN 1980 AND 1989 THEN '1980s'
        WHEN release_year BETWEEN 1990 AND 1999 THEN '1990s'
        WHEN release_year BETWEEN 2000 AND 2009 THEN '2000s'
        WHEN release_year BETWEEN 2010 AND 2020 THEN '2010s'
    END                                               AS decade,
    genre,
    COUNT(DISTINCT game_title)                        AS titles,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS sales_M
FROM game_sales
WHERE release_year IS NOT NULL AND genre IS NOT NULL
GROUP BY decade, genre
HAVING COUNT(DISTINCT game_title) >= 5
ORDER BY decade, sales_M DESC;


-- ============================================================
--  SECTION 7 — ENGAGEMENT ANALYSIS
-- ============================================================

-- 7.1 Engagement Metrics Summary
SELECT
    ROUND(AVG(plays)::NUMERIC, 0)                     AS avg_plays,
    ROUND(AVG(backlogs)::NUMERIC, 0)                  AS avg_backlogs,
    ROUND(AVG(wishlist)::NUMERIC, 0)                  AS avg_wishlist,
    ROUND(AVG(playing)::NUMERIC, 0)                   AS avg_playing,
    ROUND(AVG(times_listed)::NUMERIC, 0)              AS avg_times_listed,
    ROUND(AVG(num_reviews)::NUMERIC, 0)               AS avg_reviews,
    MAX(plays)                                        AS max_plays,
    MAX(wishlist)                                     AS max_wishlist,
    MAX(backlogs)                                     AS max_backlogs
FROM game_engagement;


-- 7.2 Top 15 Most Played Games
SELECT
    game_title,
    primary_genre,
    rating,
    plays,
    wishlist,
    backlogs,
    release_year
FROM game_engagement
ORDER BY plays DESC NULLS LAST
LIMIT 15;


-- 7.3 Top 15 Most Wishlisted Games
SELECT
    game_title,
    primary_genre,
    rating,
    wishlist,
    plays,
    backlogs
FROM game_engagement
ORDER BY wishlist DESC NULLS LAST
LIMIT 15;


-- 7.4 Engagement by Genre
SELECT
    primary_genre,
    COUNT(*)                                          AS total_games,
    ROUND(AVG(plays)::NUMERIC, 0)                     AS avg_plays,
    ROUND(AVG(wishlist)::NUMERIC, 0)                  AS avg_wishlist,
    ROUND(AVG(backlogs)::NUMERIC, 0)                  AS avg_backlogs,
    ROUND(AVG(rating)::NUMERIC, 2)                    AS avg_rating
FROM game_engagement
WHERE primary_genre IS NOT NULL
GROUP BY primary_genre
ORDER BY avg_plays DESC;


-- ============================================================
--  SECTION 8 — COMBINED INSIGHTS (Merged Data)
-- ============================================================

-- 8.1 Rating vs Sales Cross Analysis
SELECT
    rating_tier,
    COUNT(*)                                          AS total_games,
    ROUND(AVG(global_sales)::NUMERIC, 3)              AS avg_global_sales_M,
    ROUND(SUM(global_sales)::NUMERIC, 2)              AS total_sales_M,
    ROUND(AVG(CAST(plays AS FLOAT))::NUMERIC, 0)      AS avg_plays,
    ROUND(AVG(CAST(wishlist AS FLOAT))::NUMERIC, 0)   AS avg_wishlist
FROM merged_data
WHERE rating_tier IS NOT NULL
GROUP BY rating_tier
ORDER BY avg_global_sales_M DESC;


-- 8.2 Top 20 Best Selling Games with Engagement
SELECT
    m.game_title,
    m.primary_genre,
    m.rating,
    m.rating_tier,
    m.global_sales,
    m.na_sales,
    m.eu_sales,
    m.jp_sales,
    m.publisher,
    e.plays,
    e.wishlist,
    e.backlogs
FROM merged_data m
LEFT JOIN game_engagement e ON m.game_title = e.game_title
WHERE m.global_sales > 0
ORDER BY m.global_sales DESC
LIMIT 20;


-- 8.3 Hidden Gems (High Rating + Low Sales)
SELECT
    game_title,
    primary_genre,
    rating,
    global_sales,
    plays,
    wishlist,
    primary_developer
FROM merged_data
WHERE rating >= 4.2
  AND (global_sales < 1 OR global_sales IS NULL OR global_sales = 0)
  AND plays > 5000
ORDER BY rating DESC, plays DESC
LIMIT 20;


-- 8.4 Overrated Games (Low Rating + High Sales)
SELECT
    game_title,
    primary_genre,
    rating,
    global_sales,
    plays,
    publisher
FROM merged_data
WHERE rating < 3.0
  AND global_sales >= 2
ORDER BY global_sales DESC
LIMIT 15;


-- 8.5 Developer Performance
SELECT
    primary_developer,
    COUNT(*)                                          AS games_made,
    ROUND(AVG(rating)::NUMERIC, 2)                    AS avg_rating,
    ROUND((AVG(plays))::NUMERIC, 0)                   AS avg_plays,
    ROUND((SUM(plays)/1000.0)::NUMERIC, 1)            AS total_plays_K,
    MAX(rating)                                       AS best_rating
FROM game_engagement
WHERE primary_developer IS NOT NULL
  AND primary_developer != 'Unknown'
GROUP BY primary_developer
HAVING COUNT(*) >= 2
ORDER BY avg_rating DESC
LIMIT 20;


-- ============================================================
--  SECTION 9 — QUICK VIEW QUERIES
-- ============================================================

-- 9.1 Use all views at once
SELECT * FROM vw_genre_rating          LIMIT 10;
SELECT * FROM vw_platform_sales        LIMIT 10;
SELECT * FROM vw_publisher_performance LIMIT 10;
SELECT * FROM vw_yearly_trends         LIMIT 10;
SELECT * FROM vw_developer_stats       LIMIT 10;
SELECT * FROM vw_engagement_sales      LIMIT 10;


-- 9.2 Full EDA Summary in One Query
SELECT
    (SELECT COUNT(*) FROM game_engagement)            AS total_engagement_records,
    (SELECT COUNT(*) FROM game_sales)                 AS total_sales_records,
    (SELECT COUNT(*) FROM merged_data WHERE global_sales > 0) AS matched_games,
    (SELECT ROUND(AVG(rating)::NUMERIC, 2) FROM game_engagement) AS avg_rating,
    (SELECT ROUND(SUM(global_sales)::NUMERIC, 2) FROM game_sales) AS total_global_sales_M,
    (SELECT game_title FROM game_sales ORDER BY global_sales DESC LIMIT 1) AS best_selling_game,
    (SELECT platform FROM vw_platform_sales LIMIT 1)  AS top_platform,
    (SELECT publisher FROM vw_publisher_performance LIMIT 1) AS top_publisher,
    (SELECT genre FROM vw_genre_rating LIMIT 1)       AS top_rated_genre;
