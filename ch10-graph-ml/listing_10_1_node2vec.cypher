// Listing 10.1 — Node embeddings in the database (GDS)
// Needs a projected graph named 'myGraph'; run_listing_10_1.py projects the
// Chapter 7 ratings graph and runs this for you.
CALL gds.node2vec.write('myGraph', {
  embeddingDimension: 64,
  writeProperty: 'embedding'
});
