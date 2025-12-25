# OnlyBlendsMixer
"An extension to turn Blender into a Mixer... of Sounds.
It's a new Sound Node Editor to build Synthesizer's and design Audio."

<img width="1852" height="1012" alt="overview" src="https://github.com/user-attachments/assets/daf4c5b4-f44c-46dd-8a6c-5ac2a4fa0315" />

# Features

- Create samples from an oscillator node with basic waveform sine, sawtooth, square and triangle
- Edit a sample with a lot of functions:
  - 'Limit' to control the length 
  - 'Fade in / out'
  - 'Mix' and 'Modulate' to combine 2 waveforms into a new one
  - 'volume'
  - ... and many more
  - The functions are mapped from the internal aud libary documented [here](https://docs.blender.org/api/current/aud.html)

  <img width="282" height="382" alt="Bildschirmfoto vom 2025-12-20 01-40-08" src="https://github.com/user-attachments/assets/0c3faae2-f2f0-4e2d-8240-53774659b84d" />

- The Sample to Sound Node creates a blender Sound Data block which can be used with Blender's Speaker Object
- Sound's can be linked with the Speaker Link Node or you can select it in the already existing Speaker Property Panel
- The Speaker Link Node adjust the Strip length based on the sample / sound length
- Geometry to Sample
- Sample to Geometry
- Create Note Sequences and use it with a group where an 'Instrument' is defined
- a Note sequence is a list of 3D-Vectors with (frequency, duration, volume)
# How To Use ItD

https://github.com/user-attachments/assets/bdb6c43f-5aad-47e5-8b32-e78b9e9ca526

- you can find a new editor

<img width="865" height="401" alt="New_sound_editor" src="https://github.com/user-attachments/assets/ab0fbfe4-526a-4cf1-a04d-6a61ce8fd7df" />

- you can play sound’s via space bar and render the audio via Render -> Render Audio...
- create Sounds with Geometry Nodes
- <img width="1858" height="1003" alt="geometry_nodes_example" src="https://github.com/user-attachments/assets/a6e8a52e-9c6e-4a52-bde7-26c434989458" />

- Geometry To Sample
  - select the object with the geometry node modifier
  - select if you want to use the mesh or pointcloud domain
  - tip in the attribute name of the geometry domain
  - you can map the frequency from the sound editor node to a geometry node socket input
  - you can download an example blend file with a geoemtry node setup to create waveforms [here](https://ilineiros.gumroad.com/l/customwaveforms)

# Support Me

[here on PayPal](https://www.paypal.com/donate/?hosted_button_id=FGQJQHK9ZXG8G)

# Current ToDo's and Upcoming Features for 0.2

- [ ] mesh to sample node
  - [ ] reload from blend file no graph update
- [ ] if speaker pitch is changed strip length also change
- [ ] if scene fps change strip length should also change
- [ ] join / merge vector field
- [ ] copied sample to sound not working
- [ ] deleted mesh if Sample To Mesh node is deleted

- [ ] Note Node
  - [ ] selectable octave
  - [ ] duration as 1/4 1/8 etc
  - [ ] input for dpm
  - [ ] new sockets: note string 
