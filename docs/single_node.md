# Single Node

![single_node](images/single_node.png)

Retrieve a single node from the database.

```python
class A(Node): pass

results = MyDB.match(A)
```

```cypher
MATCH (a:A)
RETURN *
```
