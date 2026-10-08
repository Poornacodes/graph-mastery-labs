// Try It Yourself 4.1 — a small movie-ratings graph with constraints.
// Model: (:Viewer)-[:RATED {stars}]->(:Movie), (:Viewer)-[:FOLLOWS]->(:Viewer)
// (Viewer rather than Person keeps this lab separate from Listings 4.1–4.9.)

CREATE CONSTRAINT viewer_name IF NOT EXISTS
FOR (v:Viewer) REQUIRE v.name IS UNIQUE;
CREATE CONSTRAINT movie_title IF NOT EXISTS
FOR (m:Movie) REQUIRE m.title IS UNIQUE;

UNWIND ['Inception','Interstellar','The Matrix','Arrival','Her',
        'Blade Runner 2049','Ex Machina','Gravity','Moon','Primer'] AS t
MERGE (:Movie {title: t});

UNWIND ['Ana','Ben','Chen','Dara','Eli','Fay'] AS n
MERGE (:Viewer {name: n});

UNWIND [
  ['Ana','Inception',5],   ['Ana','The Matrix',4],   ['Ana','Her',3],
  ['Ben','Inception',5],   ['Ben','Interstellar',5], ['Ben','Arrival',4],
  ['Ben','Moon',5],        ['Chen','Interstellar',4],['Chen','Ex Machina',5],
  ['Chen','The Matrix',5], ['Chen','Primer',4],      ['Dara','Arrival',5],
  ['Dara','Her',4],        ['Dara','Gravity',2],     ['Eli','Blade Runner 2049',5],
  ['Eli','Inception',4],   ['Eli','Moon',3],         ['Fay','Gravity',3],
  ['Fay','Primer',5],      ['Fay','Ex Machina',4]
] AS r
MATCH (v:Viewer {name: r[0]}), (m:Movie {title: r[1]})
MERGE (v)-[x:RATED]->(m) SET x.stars = r[2];

UNWIND [['Ana','Ben'],['Ana','Chen'],['Ben','Dara'],['Chen','Fay'],
        ['Dara','Eli'],['Eli','Ana']] AS f
MATCH (a:Viewer {name: f[0]}), (b:Viewer {name: f[1]})
MERGE (a)-[:FOLLOWS]->(b);
