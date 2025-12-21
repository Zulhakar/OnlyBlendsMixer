# OnlyBlendsMixer
"An extension to turn Blender into a Mixer... of Sounds.
It's a new Sound Node Editor to build Synthesizer and design Audio."

<img width="1852" height="1012" alt="overview" src="https://github.com/user-attachments/assets/daf4c5b4-f44c-46dd-8a6c-5ac2a4fa0315" />

# Features

- create samples from an oscillator node with basic waveform sine, sawtooth, square and triangle
- edit a sample with a lot of functions:
  - 'limit' to control the length 
  - 'fade in / out'
  - 'mix' and 'modulate' to combine 2 waveforms to a new one
  - 'volume'
  - ... and many more
  - the functions are mapped from the internal aud libary documented [here](https://docs.blender.org/api/current/aud.html)

  <img width="282" height="382" alt="Bildschirmfoto vom 2025-12-20 01-40-08" src="https://github.com/user-attachments/assets/0c3faae2-f2f0-4e2d-8240-53774659b84d" />

- the Sample to Sound Node creates a blender Sound Data block which can be used with Blender's Speaker Object
- Sound's can be linked with the Speaker Link Node or you can select it in the allready exiting Speaker Property Panel
- The Speaker Link node adjust the Strip length based on the sample / sound length
- Geometry To Sample and Sample To Geometry

<img width="1520" height="689" alt="Sound_Nodes" src="https://github.com/user-attachments/assets/95b925d3-56c4-44bd-baf2-4edb406a7f7b" />

# How To Use It

- you can find a new editor
 
<img width="833" height="524" alt="sound_editor" src="https://github.com/user-attachments/assets/85ba3412-d1b4-4ed5-84ea-7facbeb1bb6e" />

- you can play sound's via space bar and render the audio via Render -> Render Audio...

- create Sounds with Geometry Nodes
- here is an example file https://ilineiros.gumroad.com/l/customwaveforms

# Support Me

https://ilineiros.gumroad.com/l/customwaveforms


# TODO

- [x] sequence Node (select group which need frequency socket input and sample output)
  - [x] ~~implementation like simulation zone~~
  - [x] one node with selection for existing group
  - [x] selection for frequence socket and input for note field
  - [ ] ~~rename it to instrument Zone~~
  - [x] selection for optional duration mapping to node group
- [x] New vector nodes : Vector and Combine-XYZ
- [x] Group Node, switch tree etc
  - [x] show only the possible trees in selection
  - [x] if socket is renamed in NodeGroupInput or Output change also name of the
        GroupNode equivalent Socket
  - [ ] optional: rename Socket with click on Name Label in the custom interface panel
        "Group Sockets"
  - [x] group node in node menu
  - [x] update group node sockets if socket added
  - [x] update group node sockets if removed
  - [x] update group node sockets if socket type changed
  - [x] changing the node tree changes also the sockets of group node
- [x] menu make group (~~rebuild the entire menu~~)

- [x] Note To Frequency
    - [x]  selectable note
    - [ ] optional: string input as alternative
    - [ ] optional: selection of octave
- [x] refactor and simplify node_tree update
- [x] simplify graph updates, make performance improvements
- [x] add group input / output and node group menu
- [x] hide sockets and "store" previous input value for Edit Sample Node
- [x] sample to mesh node 
- [ ] mesh to sample node
  - [x] geometry to sample with frequency input
  - [x] socket selectable via ui list
  - [ ] reload from blend file no graph update
  - [ ] optional: make a operator ui list combo like enumproperty or enumproperty
- [ ] load and save blend file tests
- [ ] copy node, override default values
- [ ] if speaker pitch is changed strip length also change
- [ ] if scene fps change strip length should also change
- [x] instrument node: if selected node tree updates the instrument should also update
- [ ] join / merge vector field
- [ ] integer sockets accept float and int float
# ALPHA Release
- [ ] alpha release todo:
  - [ ] optional: renaming stuff
  - [ ] readme update: guide github / blender extension page
  - [ ] update blender_manifest
  - [ ] sound examples: techno 
  - [x] geoemtry node example with waveform generator
  - [ ] screen shots
  - [ ] optional: logo
  - [ ] limit oscillator output, or return only one period
# Bugs
- plug note sequence output into group output -> no 
- group node gets 2x sockets
- copied sample to sound not working
- deleted mesh if Sample To Mesh node is deleted
- limit oscillator or limit in Sample To Sound node etc or check for duration / length
# 0.2
- [ ] Note Node
  - [ ] selectable octave
  - [ ] duration as 1/4 1/8 etc
  - [ ] input for dpm
  - [ ] new sockets: note string 
