// Load the graph in the Gremlin console (or run gremlin_lab.py)
g.addV('Person').property('name','Alice').as('a').
  addV('Person').property('name','Bob').as('b').
  addV('Person').property('name','Carol').as('c').
  addV('Person').property('name','Dave').as('d').
  addE('knows').from('a').to('b').addE('knows').from('b').to('c').
  addE('knows').from('a').to('d').addE('knows').from('d').to('c').iterate()
