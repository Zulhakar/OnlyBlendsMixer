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
- [ ] Group Node, switch tree etc
  - [x] show only the possible trees in selection
  - [ ] if socket is renamed in NodeGroupInput or Output change also name of the
        GroupNode equivalent Socket
  - [ ] rename Socket with click on Name Label in the custom interface panel
        "Group Sockets"
  - [x] group node in node menu
  - [x] update group node sockets if socket added
  - [x] update group node sockets if removed
  - [x] update group node sockets if socket type changed
  - [x] changing the node tree changes also the sockets of group node
- [x] menu make group (~~rebuild the entire menu~~)
- [ ] Note Node
  - [ ] selectable octave
  - [ ] duration as 1/4 1/8 etc
  - [ ] input for dpm
  - [ ] new sockets: note string 
- [x] Note To Frequency
    - [x]  selectable note
    - [ ] optional: string input as alternative
    - [ ] optional: selection of octave
- [ ] refactor and simplify node_tree update
- [ ] simplify graph updates, make performance improvements
- [x] add group input / output and node group menu
- [ ] hide sockets and "store" previous input value for Edit Sample Node
- [ ] sample to mesh node 
- [ ] mesh to sample node
  - [x] geometry to sample with frequency input
  - [x] socket selectable via ui list
  - [ ] reload from blend file no graph update
  - [ ] optional: make a operator ui list combo like enumproperty or enumproperty
- [ ] load and save blend file tests
- [ ] copy node, override default values
- [ ] if speaker pitch is changed strip length also change
- [ ] if scene fps change strip length should also change
