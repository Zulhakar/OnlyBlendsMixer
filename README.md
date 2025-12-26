# OnlyBlendsMixer
"An extension to turn Blender into a Mixer... of Sounds.
It's a new 'Sound Node' Editor to build Synthesizer's and design Audio."
## Prototype V0.1

<img width="1852" height="1012" alt="overview" src="https://github.com/user-attachments/assets/daf4c5b4-f44c-46dd-8a6c-5ac2a4fa0315" />

# Features

- Create samples from an 'Oscillator' node with basic waveforms: Sine, Sawtooth, Square and Triangle
- Edit a sample with a lot of functions:
  - 'Limit' to control the length 
  - 'Fade in / out'
  - 'Mix' and 'Modulate' to combine 2 waveforms into a new one
  - 'Volume'
  - ... and many more
  - The functions are mapped from the internal aud libary documented [here](https://docs.blender.org/api/current/aud.html)

  <img width="282" height="382" alt="Bildschirmfoto vom 2025-12-20 01-40-08" src="https://github.com/user-attachments/assets/0c3faae2-f2f0-4e2d-8240-53774659b84d" />

- The 'Sample to Sound' Node creates a blender Sound Data block which can be used with Blender's Speaker Object
- Sound's can be linked with the 'Speaker Link' Node or you can select it in the already existing Speaker Property Panel
- The Speaker Link Node adjusts the Strip length based on the sample / sound length
- 'Geometry to Sample' Node
- 'Sample to Mesh' Node
- Create music note sequences and use it with a group where an 'Instrument' is defined
- A Note sequence is a list of 3D-Vectors with (Frequency, Duration, Volume)
# How To Use It

https://github.com/user-attachments/assets/bdb6c43f-5aad-47e5-8b32-e78b9e9ca526

- You can find a new editor as seen below

<img width="865" height="401" alt="New_sound_editor" src="https://github.com/user-attachments/assets/ab0fbfe4-526a-4cf1-a04d-6a61ce8fd7df" />

- You can play sound’s via space bar and render the audio via Render -> Render Audio...
- Create Sounds with Geometry Nodes
- <img width="1858" height="1003" alt="geometry_nodes_example" src="https://github.com/user-attachments/assets/a6e8a52e-9c6e-4a52-bde7-26c434989458" />

- 'Geometry To Sample'
  - Select the Geometry Node Group (Modifier) ->
  - Select if you want to use the Domain 'Mesh' or 'Point Cloud' ->
  - Tip in the Attribute name of the Geometry domain, from here on you can:
  - Map the frequency from the 'Sound Editor' Node to a Geometry Node socket input
  
  - If you'd like, download an example .blend with a Geoemtry Node Setup to create waveforms [here](https://github.com/Zulhakar/OnlyBlendsMixer/blob/main/geometry_node_example.blend)

- 'Instrument' Node

https://github.com/user-attachments/assets/5b97b3b0-9dc3-4ed0-8908-115beef1684b


# Support Me

[here on PayPal](https://www.paypal.com/donate/?hosted_button_id=FGQJQHK9ZXG8G), other ways for support are work in progress.
At the point of release, I've been working on and off on "OnlyBlends Mixer" for the better part of the last five months with it being only my second Blender Extension.
These donations are purely for the purpose of showing appreciation for my work and aiding in further development.

[here](https://ilineiros.gumroad.com/l/customwaveforms) (Gumroad is work in progress)

# Current ToDo's and Upcoming Features for 0.2

- [ ] 'Mesh to Sample' Node 
  - [ ] Reload from .blend doesn't perform a graph update
- [ ] If 'Speaker pitch' is changed 'Strip length' also changes
- [ ] If 'Scene FPS' changes 'Strip length' should also change
- [ ] Join / Merge vector field
- [ ] Copied 'Sample to Sound' not working
- [ ] Also deletes Mesh if 'Sample To Mesh' Node is deleted
- [ ] ...

- [ ] 'Note Node'
  - [ ] Selectable Octave
  - [ ] Duration as 1/4 , 1/8 etc.
  - [ ] Input for BPM
  - [ ] New sockets: 'Note string'

