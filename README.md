# OnlyBlendsMixer 0.5.1 Alpha
"An extension to turn Blender into a Mixer... of Sounds.
It's a new 'Sound Node' Editor to build Synthesizer's and design Audio."
## Prototype V2

![overview](https://github.com/user-attachments/assets/daf4c5b4-f44c-46dd-8a6c-5ac2a4fa0315)
# Features

- Create samples from an 'Oscillator' node with basic waveforms: Sine, Sawtooth, Square and Triangle
- Edit a sample with a lot of functions:
  - 'Limit' to control the length 
  - 'Fade in / out'
  - 'Mix' and 'Modulate' to combine 2 waveforms into a new one
  - 'Volume'
  - ... and many more
  - The functions are mapped from the internal aud libary documented [here](https://docs.blender.org/api/current/aud.html)


![edit_sample](https://github.com/user-attachments/assets/bbf8efb9-b75d-41f2-a23d-bbaa0503e85e)

- The 'Sample to Sound' Node creates a blender Sound Data block which can be used with Blender's Speaker Object
- Sound's can be linked with the 'Speaker Link' Node or you can select it in the already existing Speaker Property Panel
- The Speaker Link Node adjusts the Strip length based on the sample / sound length

## Geometry Node Link

- The 'Geometry Modifier Object' Node can manipulate the Input of an Geometry Nodes Modifier
- You can send Data from Mixer Nodes to Geometry Nodes. As an example: To adjust a waves frequency
  
![GeometryModifierObject](https://github.com/user-attachments/assets/830d2b7a-520c-4863-8a00-99bdc1de1272)
- The 'Object to Sample' Node gets Data from Geometry / Objects an creates a Sound Sample
- You could use Blender Objects to play/create sounds

![Object_to_Sample](https://github.com/user-attachments/assets/83ba9d88-8158-4f50-ad3f-58aa7ed1b55b)
## MIDI Import

- New experimental Feature "Import MIDI" Node
- "MIDI to Track Object" Node to get Note_On, Note_Off events from MIDI files, (more events coming soon)
- The resulting Object from the "MIDI to Track Object" can be converted to "Sample" with "Track Sample" Node
- You can observe the Object from "MIDI to Track Object" to see how a Note Sequence are processed from "Track Sample" Node
- It is possible to create the Notes via Geometry Nodes and MIDI is merely an additonal Feature
- The Data needed for a "Track Sample" node should have the following attributes: Position.X -> Start_Time, Position.Y -> Duration, Position.Z -> Frequency and Volume

![Midi_data](https://github.com/user-attachments/assets/f3c59045-f382-40e0-ab8a-42131c37b530)
   
# Support Me

[![pay_pal_icon](https://github.com/user-attachments/assets/4b007169-56f8-4f20-9015-cb138cc2e0ff)](https://www.paypal.com/donate/?hosted_button_id=FGQJQHK9ZXG8G)

[Here on PayPal](https://www.paypal.com/donate/?hosted_button_id=FGQJQHK9ZXG8G), other ways for support are work in progress.
At the point of release, I've been working on and off on "OnlyBlends Mixer" for the better part of the last five months with it being only my second Blender Extension.
These donations are purely for the purpose of showing appreciation for my work and aiding in further development.

[Here on Gumroad](https://ilineiros.gumroad.com/l/customwaveforms) (Gumroad is work in progress)

### If you wish to you could join my Discord server

[![discord_icon_64x64](https://github.com/user-attachments/assets/77cbeca8-e9c1-4b2f-9fff-a3c11b3f8cae)](https://discord.gg/rxut2MfZTM)
# Upcoming Features

- Support for more Midi Events

# Changelog
## v0.1.2 Hotfix
  - [x] Fixed copy function of Nodes, where "CTRL+V" of nodes caused Blender to crash
## v0.1.3 Hotfix
  - [x] Loading a .blend file containing Mixer nodes should now work better
  - [x] Oscillator Nodes and 'Geometry to Sample' Nodes update the Node tree after loading the .blend file.
  - [X] General fix for 'Geometry to Sample' Node
  
## 0.5.1
  - Complete Refactor
  - The basic Node functions moved to OnlyBlends.Core https://github.com/Zulhakar/OnlyBlendsCore
  - MIDI Import
  - MIDI to Track
  - Track Sample
  - Import Sound Node
  - Sound To Sample Node
  - Removed "Instrument Node" -> Use "Track Sample" Node
  - Connection to Geometry Nodes via "Geometry Modifier Object" and "Object To Sample"
