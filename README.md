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
- Transfer normals script based on Vrav's Transfer Vertex Normals
  
================================================================  
  
*Changelog:*  
  
v0.0.3  
- rewrote transfer vertex normals for speed + compatibility
- ui fixes/optimizations
- generation speed optimizations
- changed way the script detects normals to use
- added Flat generation mode (split normals only)
- removed some unneeded variables  
  
v0.0.2  
- added transfer functionality to ui panel
- menu usability optimizations
- added license
- moved variables back to init file
- changed pie menu icons
  
v0.0.1  
- initial upload  
  