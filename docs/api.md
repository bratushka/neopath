Query methods:

```python
.match
.connected_through  # .con_thru
.where
```

`.match` argument types:
```python
None
str
Logic
Type[Node]
Node
Condition
```

`.con_thru` argument types:
```python
None
str
Logic
Type[Edge]
Edge
Condition
```

`.where` argument types:
```python
str
Logic
Condition
```

Compiled `.match`:

|Arg type|python|cypher|
|---|---|---|
|None|`.match()`|`MATCH (a)`|
|str|`.match('Human')`|`MATCH (a:Human)`|
|Type[Node]|`.match(Human)`|`MATCH (a:Human)`|
|Node|`.match(human)`|`MATCH (a)`<br/>`WHERE a.uid = 123`|
|And|`.match(Human & 'Male')`|`MATCH (a)`<br/>`WHERE (a:Human AND a:Male)`|
|Or|`.match(Human ⎮ 'Tree')`|`MATCH (a)`<br/>`WHERE (a:Human OR a:Male)`|
|Xor|`.match(Human ^ 'Tree')`|`MATCH (a)`<br/>`WHERE (a:Human XOR a:Male)`|
|Not|`.match(~Human)`|`MATCH (a)`<br/>`WHERE (NOT a:Human)`|
|Condition|`.match(Human.age >= 18)`|`MATCH (a)`<br/>`WHERE (a:Human AND a.age >= 18)`|

Compiled `.connected_through`:

|Arg type|python|cypher|
|---|---|---|
|None|`.con_thru()`|`MATCH ()-[b]-()`|
|str|`.con_thru('Loves')`|`MATCH -[b:Loves]-`|
|Type[Node]|`.con_thru(Loves)`|`MATCH [b:LOVES]`|
|Node|`.con_thru(loves)`|`MATCH [b:LOVES]`<br/>`WHERE b.uid = 123`|
|Or|`.con_thru(Loves ⎮ 'Hates')`|`MATCH [b:LOVES⎮:Hates]`|
|Xor|`.con_thru(Loves ^ 'Hates')`|`MATCH [b:LOVES⎮:Hates]`|
|Not|`.con_thru(~Loves)`|`MATCH [b]`<br/>`WHERE (NOT type(b) = 'LOVES')`|
|Condition|`.con_thru(Loves.how == 'platonically')`|`MATCH [b:LOVES]`<br/>`WHERE (b.how = 'platonically')`|

Compiled `.where` after a `.match(Human)`:

|Arg type|python|cypher|
|---|---|---|
|str|`.where('blah.blah = "blah"')`|`MATCH (a)`<br/>`WHERE blah.blah = "blah"`|
|And|`.where()`||
|Or|`.where()`||
|Xor|`.where()`||
|Not|`.where()`||
|Condition|`.where()`||

```python
.match()                     # MATCH (a)
.match('Human')              # MATCH (a:Human)
.match(Human)                # MATCH (a:Human)

.match(human)                # MATCH (a:Human)
                             # WHERE a.uid = 123

.match(Human & 'Tree')       # MATCH (a:Human:Tree)

.match(Human | 'Tree')       # MATCH (a)
                             # WHERE (a:Human OR a:Tree)

.match(Human ^ 'Tree')       # MATCH (a)
                             # WHERE (a:Human XOR a:Tree)

.match(human | other_human)  # MATCH (a:Human)
                             # WHERE a.uid = 123 OR a.uid = 124)

.match(~Human)               # MATCH (a)
                             # WHERE (NOT a:Human)
```

```python
.con_thru()                 # MATCH ()-[b]-()
.con_thru('Loves')          # MATCH ()-[b:Loves]-()
.con_thru(Loves)            # MATCH ()-[b:LOVES]-()

.con_thru(loves)            # MATCH ()-[b:LOVES]-()
                            # WHERE b.uid = 123

.con_thru(Loves | 'Hates')  # MATCH p = ()-[:LOVES|:Hates]-()
                            # WITH *, relationships(p)[0] as b

.con_thru(~Loves)           # MATCH ()-[b]-()
                            # WHERE type(b) <> 'Loves'

.con_thru(~loves)           # MATCH ()-[b]-()
                            # WHERE NOT (type(b) = 'Loves' AND b.uid = 123)
```
