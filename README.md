# Blender-Normal-Editing-Tools
  
Normals editor for Blender 2.74+
  
  
*WIP*, wiki will be updated to reflect current changes soon  
  
================================================================  
  
*Features:*  
- Normals editor for split and vertex normals
- Manual Editing by input vector or a rotating arrow object
- Automatic generation of normals using different presets:
  - allows generating normals for selected vertices, faces, or the selected mesh
  - supported methods:
    - *Default*
    - *Bent* from cursor location
	- *Smooth* (average of connected/selected face normals)
	- *Weighted* (using face areas as weights)
	- *Flat* (if using split normals)
	- *Transfer* (originally based on Vrav's Transfer Vertex Normals)
  - Pie menu with auto-generate presets and mode switcher
    - bound to Mouse Button 4 by default, set up in '__init__.py'
    - refer to 'keyslist.txt' for key names
    - search for: 'kmi = km.keymap_items.new('wm.call_menu_pie', 'BUTTON4MOUSE', 'PRESS')'  
  
================================================================  
  
*Changelog:*  
  
1.0.3 (current)  
- performance optimization: removed function call to create normals data  
   
1.0.2  
- Transfer now takes split normals into account for source objects (if available)
- removed last instance of average calculation, removed an unused variable in transfer functions  
  
1.0.1
- removed old face index variable
- added new mode enum to cleanup  
  
1.0.0  
- *New Feature*:
  - added new manual edit mode using a manipulator object
- *General Code Cleanup*:
  - removed some unused variables left over from testing features
  - removed unneeded average calculations (let normalization handle it)
  - created common functions to build mesh data used by all other functions
  - switched vertex normal editing to bmesh
- *UI*:
  - moved shared selection-related variables to data (top) tab
  - Generate panel overhaul - back to ENUM to save UI space
- *Generate*:
  - added weighted normals mode (by connected face areas)  
  
0.0.7
- fixed ridiculous memory usage + half-working split normals transfer caused by typos  
  
0.0.6    
- overhauled Transfer functions:
  - transfer should no longer reset existing normals
  - fixed weird behavior with 'selected only' enabled
  - created specialized version of the function for split normals
  - added toggle to use face selection instead of vertex selection while using split normals  
  
0.0.5  
- fixed Default Auto-generate mode for split normals in Blender 2.75 (change should also work in older versions)
- tooltip text fixes
- consolidated pie menu and other functions into one file, removed unneeded temp_data file
- added a function to flip normals on selected object
- pie menu is now only for Auto-Generate modes, no more bad attempt at nested pie menus :)  
  
0.0.4  
- moved Transfer tool to Auto-Generate section of panel
- Transfer mode updated to use the Selected Only toggle to generate for selection
- consolidated variables  
  
0.0.3  
- rewrote transfer vertex normals for speed + compatibility
- ui fixes/optimizations
- generation speed optimizations
- changed way the script detects normals to use
- added Flat generation mode (split normals only)
- removed some unneeded variables  
  
0.0.2  
- added transfer functionality to ui panel
- menu usability optimizations
- added license
- moved variables back to init file
- changed pie menu icons
  
0.0.1  
- initial upload  
  