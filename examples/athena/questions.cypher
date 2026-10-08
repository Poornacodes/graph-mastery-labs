// Listing E.4 — The four competency questions in Cypher
// Q1: who leads the project a person works on?
MATCH (p:Entity {name:$person})-[:REL {type:'WORKS_ON'}]->(proj)
      <-[:REL {type:'LEADS'}]-(lead)
RETURN lead.name AS project_lead, proj.name AS project;

// Q2: projects depending (transitively) on a component a given team builds
MATCH (t:Entity {name:$team})-[:REL {type:'BUILDS'}]->(c)
MATCH (proj)-[:REL*1..5 {type:'DEPENDS_ON'}]->(c)
WHERE proj.type = 'Project'
RETURN DISTINCT proj.name AS dependent_project, c.name AS component;

// Q3: public announcements about a product + who worked on it
MATCH (prod:Entity {name:$product})
OPTIONAL MATCH (prod)<-[:REL {type:'ANNOUNCES'}]-(ann)
OPTIONAL MATCH (person)-[:REL {type:'WORKS_ON'}]->(:Entity)
               -[:REL*0..2]-(prod)
RETURN collect(DISTINCT ann.name) AS announcements,
       collect(DISTINCT person.name) AS contributors;

// Q4: people within 2 hops of a departed employee on a critical project
MATCH (dep:Entity {name:$departed})-[:REL*1..2]-(near:Entity)
WHERE near.type = 'Person'
RETURN DISTINCT near.name AS at_risk_contact;
