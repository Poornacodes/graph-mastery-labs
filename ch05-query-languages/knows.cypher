// "Alice knows Bob knows Carol; Alice knows Dave knows Carol"
UNWIND ['Alice','Bob','Carol','Dave'] AS n
MERGE (:Person {name: n});
UNWIND [['Alice','Bob'],['Bob','Carol'],['Alice','Dave'],['Dave','Carol']] AS k
MATCH (a:Person {name:k[0]}), (b:Person {name:k[1]})
MERGE (a)-[:KNOWS]->(b);
