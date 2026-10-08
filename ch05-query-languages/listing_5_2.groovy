// Listing 5.2 — Gremlin: the same two questions
// Direct: start at all vertices, keep Alice, walk out 'knows', get names
g.V().has('Person','name','Alice').out('knows').values('name')

// Friend-of-friend
g.V().has('Person','name','Alice').
  out('knows').out('knows').dedup().values('name')
