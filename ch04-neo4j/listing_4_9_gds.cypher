// Listing 4.9 — PageRank and community detection with GDS
// 1. Project a named in-memory graph; friendship is symmetric,
//    so project FRIEND as undirected
CALL gds.graph.project('social', 'Person',
  {FRIEND: {orientation: 'UNDIRECTED'}});

// 2. Run PageRank, writing scores back as a node property
CALL gds.pageRank.write('social', {writeProperty: 'pagerank'})
YIELD nodePropertiesWritten;

// 3. Louvain community detection
CALL gds.louvain.stream('social')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS person, communityId
ORDER BY communityId;

// 4. Free the projection when done
CALL gds.graph.drop('social');
