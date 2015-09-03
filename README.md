# Blender-Normal-Editing-Tools
  
Normals editor for Blender 2.74+
  
  
*WIP*, initial documentation coming after everything is organized  
  
================================================================  
  
*Features:*  
- Normals editor with support for split and vertex normals
- Supports manual editing and several methods to automatically generate normals via panel ui
- Pie menu with auto-generate presets
  - bound to Mouse Button 4 by default, set up in '__init__.py'
  - refer to 'keyslist.txt' for key names
  - the line to change is:
  - 'kmi = km.keymap_items.new('wm.call_menu_pie', 'BUTTON4MOUSE', 'PRESS')'
- Transfer normals script based on Vrav's Transfer Vertex Normals
  
================================================================  
  
*Changelog:*  
  
v0.0.6 (current)  
- overhauled Transfer functions:
  - transfer should no longer reset existing normals
  - fixed weird behavior with 'selected only' enabled
  - created specialized version of the function for split normals
  - added toggle to use face selection instead of vertex selection while using split normals  
  
v0.0.5  
- fixed Default Auto-generate mode for split normals in Blender 2.75 (change should also work in older versions)
- tooltip text fixes
- consolidated pie menu and other functions into one file, removed unneeded temp_data file
- added a function to flip normals on selected object
- pie menu is now only for Auto-Generate modes, no more bad attempt at nested pie menus :)  
  
v0.0.4  
- moved Transfer tool to Auto-Generate section of panel
- Transfer mode updated to use the Selected Only toggle to generate for selection
- consolidated variables  
  
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
  