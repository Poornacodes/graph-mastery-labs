// Try It Yourself 4.1 — solutions.

// Q1. The movies Ana rated five stars
MATCH (:Viewer {name:'Ana'})-[r:RATED]->(m:Movie)
WHERE r.stars = 5
RETURN m.title AS five_star;

// Q2. The average rating per movie
MATCH (:Viewer)-[r:RATED]->(m:Movie)
RETURN m.title AS movie, round(avg(r.stars), 2) AS avg_stars,
       count(r) AS ratings
ORDER BY avg_stars DESC, movie;

// Q3. The payoff: recommend to Ana what the people she follows have watched
// (and liked) but she has not
MATCH (me:Viewer {name:'Ana'})-[:FOLLOWS]->(friend)-[r:RATED]->(m:Movie)
WHERE r.stars >= 4 AND NOT (me)-[:RATED]->(m)
RETURN m.title AS recommendation, collect(friend.name) AS because,
       count(*) AS votes
ORDER BY votes DESC, recommendation;
