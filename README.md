# OnlyBlendsMixer
Creating Sounds with Geometry Nodes


# TODO

- [x] sequence Node (select group which need frequency socket input and sample output)
  - [x] ~~implementation like simulation zone~~
  - [x] one node with selection for existing group
  - [x] selection for frequence socket and input for note field
  - [ ] ~~rename it to instrument Zone~~
  - [x] selection for optional duration mapping to node group
- [x] New vector nodes : Vector and Combine-XYZ
- [x] Note Sequence Node (maybee rename it)
- [ ] simplify node_tree update
- [ ] simplify graph updates, make performance improvements
- [ ] group node, switch tree etc
  - [x] show only the possible trees in selection
  - [ ] if socket is renamed in NodeGroupInput or Output change also name of the
        GroupNode equivalent Socket
  - [ ] rename Socket with click on Name Label in the custom interface panel
        "Group Sockets"
  - [ ] ...
- [ ] add group input / output and node group menu
- [ ] hide sockets and "store" previous input value for Edit Sample Node
- [ ] add / remove socket -> add missing stuff
- [ ] sample to mesh node 
- [x] mesh to sample node
  - [x] geometry to sample with frequency input
  - [x] socket selectable via ui list
  - [ ] optional: make a operator ui list combo like enumproperty or enumproperty
- [ ] menu make group (rebuild the entire menu)
- [ ] load and save blend file tests
