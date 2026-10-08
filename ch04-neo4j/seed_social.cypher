// Sample data so Listings 4.1–4.9 return results.
// People, the companies they work at, and a FRIEND network ending at Zoe.
MERGE (acme:Company {name:'Acme'})
MERGE (globex:Company {name:'Globex'})
WITH acme, globex
UNWIND [
  {name:'Alice', age:30, co:'Acme'},  {name:'Bob',   age:34, co:'Acme'},
  {name:'Carol', age:27, co:'Acme'},  {name:'Dave',  age:41, co:'Globex'},
  {name:'Erin',  age:23, co:'Globex'},{name:'Frank', age:38, co:'Acme'},
  {name:'Grace', age:29, co:'Acme'},  {name:'Heidi', age:45, co:'Acme'},
  {name:'Ivan',  age:31, co:'Acme'},  {name:'Judy',  age:26, co:'Acme'},
  {name:'Mallory',age:36,co:'Acme'},  {name:'Niaj',  age:33, co:'Acme'},
  {name:'Oscar', age:39, co:'Acme'},
  {name:'Zoe',   age:28, co:'Globex'}
] AS row
MERGE (p:Person {name: row.name}) SET p.age = row.age
WITH p, row
MATCH (c:Company {name: row.co})
MERGE (p)-[:WORKS_AT {since: 2020}]->(c);

UNWIND [['Alice','Bob'],['Bob','Carol'],['Carol','Dave'],['Dave','Zoe'],
        ['Alice','Erin'],['Erin','Frank'],['Frank','Grace'],
        ['Grace','Heidi'],['Bob','Ivan'],['Ivan','Judy'],
        ['Judy','Mallory'],['Mallory','Niaj']] AS pair
MATCH (a:Person {name: pair[0]}), (b:Person {name: pair[1]})
MERGE (a)-[:FRIEND]->(b);
