# OnlyBlendsMixer
Creating Sounds with Geometry Nodes


# TODO

Namimg and Structure

- [ ] Sample, Sound, SampleEditNode
- [ ] separate Nodes to Folder and sub_python_files
- [ ] reorder Socket to separate folder and python files

SampleEditNode

-[ ] save last state of function, links are not vanishing after changing the function

SampleToSound
-[x] update file after another node changing etc 
-[ ] file chooser or other way to create file path (brainstorming)
-[ ] handle different file types
    -[ ] selection between filetype options default wav or something
  

All Nodes

-[ ] copy from another node should work and create a new instance of Sample etc
- [ ] correct mute function
  - [ ] SampleEditNode
- [ ] error handling for wrong links
- [ ] default linking method if node added on link (find out how to modify it)

New Nodes
- [X] Notes -> value with correct frequency
- [ ] SpeakerNode
  - [x] create SpeakerSocket
  - [x] create action automatically
  - 