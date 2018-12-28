# Path With Cycle

![path_with_cycle](images/path_with_cycle.png)

Retrieve a path with a cycle in the middle.

```python
class A(Node): pass
class B(Node): pass
class C(Node): pass
class D(Node): pass
class Loves(Edge): pass
class Hates(Edge): pass

results = (MyDB
    .match(A)
    .connected_through(Loves)
    .to(B, 'b')
    .connected_through(Loves, 'b_loves_c')
    .to(C, 'c')
    .connected_through(Hates)
    .to('b')
    .connected_through('b_loves_c')
    .to('c')
    .connected_through(Hates)
    .to(D)
)
```

```cypher
MATCH
  (a:A)-[d:LOVES]->(b:B),
  (b)-[b_loves_c:LOVES]->(c:C),
  (c)-[e:HATES]->(b),
  (c)-[f:HATES]->(g:D)
RETURN *
```
