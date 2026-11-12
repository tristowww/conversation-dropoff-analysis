-- Table turns contains numeric response metrics, not transcript text.
-- Each conversation_id + turn is unique. Each row is one participant response.
SELECT cohort, turn, COUNT(*) AS n, AVG(words) AS mean_words
FROM turns
GROUP BY cohort, turn
ORDER BY cohort, turn;
