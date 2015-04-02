# Blender-Normal-Editing-Tools
  
Normals editor for Blender 2.74.
  
  
*WIP*, initial documentation coming after everything is organized  
  
================================================================  
  
*Features:*  
- Normals editor with support for split and vertex normals
- Pie menu for manual editing and auto-generate presets
  - currently bound to Mouse Button 4, set up in '__init__.py'
  - refer to 'keyslist.txt' for key names to use if changing
  - the line to change is:
  - 'kmi = km.keymap_items.new('wm.call_menu_pie', 'BUTTON4MOUSE', 'PRESS')'
- Support for Vrav's Transfer Vertex Normals addon  
  
================================================================  
  
*Changelog:*  

v0.0.2  
- added transfer functionality to ui panel
- menu usability optimizations
- added license
- moved variables back to init file
- changed pie menu icons
  
v0.0.1  
- initial upload  
  