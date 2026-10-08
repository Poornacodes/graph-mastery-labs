// Listing 5.1 — Cypher: direct and friend-of-friend
// Direct
MATCH (:Person {name:'Alice'})-[:KNOWS]->(friend)
RETURN friend.name;

// Friend-of-friend
MATCH (:Person {name:'Alice'})-[:KNOWS]->()-[:KNOWS]->(fof)
RETURN DISTINCT fof.name;
