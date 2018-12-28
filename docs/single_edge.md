# Single Edge

![single_edge](images/single_edge.png)

Retrieve 2 nodes connected by an edge.

```python
class A(Node): pass
class B(Node): pass
class Loves(Edge): pass

results = (MyDB
    .match(A)
    .connected_through(Loves)
    .to(B)
)
```

```cypher
MATCH (a:A)-[b:LOVES]->(c:B)
RETURN *
```
