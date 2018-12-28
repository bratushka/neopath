# Cycle

![image](images/cycle.png)

Retrieve 2 nodes connected by 2 edges.

```python
class A(Node): pass
class B(Node): pass
class Loves(Edge): pass
class Hates(Edge): pass

results = (MyDB
    .match(A, 'a')
    .connected_through(Loves)
    .to(B)
    .connected_through(Hates)
    .by('a')
)
```

```cypher
MATCH
  (a:A)-[b:LOVES]->(c:B),
  (c)-[d:LOVES]->(e:C)
RETURN *
```
