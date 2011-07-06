"""
Bake Layer Window main UI

Tyler Good 2011 tylergood@tylergood.net
"""

import os

import pymel.core as pmc
import maya.OpenMaya as OpenMaya

import bake_layer_tool
import quick_edit_window
import utils


class BakeLayerWindow( object ):
  """
  Main UI window for interacting with bake layers.
  """
  def __init__(self, *args, **kwargs ):
    
    # Make sure that the bakeLayer plugin is loaded
    if not ( pmc.pluginInfo( 'bake_layer_init.py', q = True, loaded = True ) ):
      raise Exception( 'Bake Layer Plugin is not currently loaded' )
    
    # Create the MEL Global var for the currently selected bake layer
    
    pmc.MelGlobals.initVar('string[]', 'selected_bake_layers')
      
    
    self.__window = pmc.window( self,
                                title = "Bake Layer Editor" )
    
    pmc.scriptJob( permanent = True,
                   parent = self.__window,
                   event = [ 'NewSceneOpened', self.new_scene ] )
    
    pmc.scriptJob( permanent = True,
                   parent = self.__window,
                   event = [ 'SceneOpened', self.open_scene ] )
                   
                   
    
    self.menu_dict = { }
    
    self.build( )
    
    self.refresh( )
    
    self.__window.show( )

  def build(self):
    self.build_menu_bar( )
    
    # Form layout for rest of window
    self.__form = pmc.formLayout( )
    
    # Buttons for quick access to things
    # TODO: Enable layer ordering
    btn_move_layer_up = pmc.symbolButton( image = 'moveLayerUp.png',
                                          annotation = 'Move Layer up',
                                          command = self.move_layer_up,
                                          enable = False )
    
    btn_move_layer_down = pmc.symbolButton( image = 'moveLayerDown.png',
                                            annotation = 'Move Layer down',
                                            command = self.move_layer_down,
                                            enable = False )
    
    btn_new_empty_layer = pmc.symbolButton( image = 'newLayerEmpty.png',
                                            annotation = 'New Empty Bake Layer',
                                            command = self.new_empty )
    
    btn_new_selected_layer = pmc.symbolButton( image = 'newLayerSelected.png',
                                               annotation = 'New Bake Layer from Selection',
                                               command = self.new_selected )
    
    
    pmc.setParent( self.__form )
     
    self.__layer_tree = pmc.treeView( parent = self.__form,
                                      width = 350,
                                      abr = False,
                                      numberOfButtons = 3 )
    
    pmc.treeView( self.__layer_tree,
                  e = True,
                  selectCommand = self.button_layer_select )
    
    pmc.treeView( self.__layer_tree,
                  e = True,
                  elc = self.button_layer_editor_rename ) 
    
    pmc.treeView( self.__layer_tree,
                  e = True,              
                  pc = ( 1, self.button_type_change ) )
                  
    pmc.treeView( self.__layer_tree,
                  e = True,
                  pc = ( 2, self.button_connection_edit ) )
    
    pmc.treeView( self.__layer_tree,
                  e = True,
                  pc = ( 3, self.button_quick_edit_window ) )
    
    left_click_menu = pmc.popupMenu( button = 3, parent = self.__layer_tree )

    pmc.treeView( self.__layer_tree,
                  e = True,
                  contextMenuCommand = pmc.CallbackWithArgs( self.show_left_click_menu,
                                                             left_click_menu ) )
  
    
    
    self.__form.attachForm( btn_new_selected_layer, 'top', 1 )
    self.__form.attachForm( btn_new_selected_layer, 'right', 2 )
    self.__form.attachNone( btn_new_selected_layer, 'bottom' )
    self.__form.attachNone( btn_new_selected_layer, 'left' )
    
    self.__form.attachForm( btn_new_empty_layer, 'top', 1 )
    self.__form.attachControl( btn_new_empty_layer, 'right', 1, btn_new_selected_layer )
    self.__form.attachNone( btn_new_empty_layer, 'bottom' )
    self.__form.attachNone( btn_new_empty_layer, 'left' )
    
    self.__form.attachForm( btn_move_layer_down, 'top', 1 )
    self.__form.attachControl( btn_move_layer_down, 'right', 4, btn_new_empty_layer )
    self.__form.attachNone( btn_move_layer_down, 'bottom' )
    self.__form.attachNone( btn_move_layer_down, 'left' )
    
    self.__form.attachForm( btn_move_layer_up, 'top', 1 )
    self.__form.attachControl( btn_move_layer_up, 'right', 1, btn_move_layer_down )
    self.__form.attachNone( btn_move_layer_up, 'bottom' )
    self.__form.attachNone( btn_move_layer_up, 'left' )
    
    self.__form.attachControl( self.__layer_tree, 'top', 1, btn_new_empty_layer )
    self.__form.attachForm( self.__layer_tree, 'left', 0 )
    self.__form.attachForm( self.__layer_tree, 'bottom', 0 )
    self.__form.attachForm( self.__layer_tree, 'right', 0 )

  
  def build_menu_bar( self ):
    self.__menu_bar = pmc.menuBarLayout( )
    
    # Build the individual menus
    self.build_layers_menu( )
    self.build_options_menu( )
    # self.build_help_menu( ) ## Not implementing this for a while
    
  def build_layers_menu( self ):
    
    self.menu_dict[ 'layers' ] = { }
    
    pmc.setParent( menu = True )
    menu = pmc.menu( label = 'Layers', allowOptionBoxes = True )
    
    menu.postMenuCommand( self.display_layers_menu )
    
    pmc.menuItem( label = 'Create Empty Layer',
                  command = self.new_empty )
    
    pmc.menuItem( label = 'Create Layer from Selected',
                  command = self.new_selected )
    
    pmc.menuItem( divider = True )
    
    pmc.menuItem( label = 'Select Objects in Selected Layers',
                  command = self.select_objects )
    pmc.menuItem( label = 'Add Selected Objects to Selected Layers',
                  command = self.add_objects )
    pmc.menuItem( label = 'Remove Selected Objects from Selected Layers',
                  command = self.remove_objects )

    pmc.menuItem( divider = True )

    pmc.menuItem( label = 'Delete Selected Layers',
                  command = self.delete_selected )
    pmc.menuItem( label = 'Delete Unused Layers',
                  command = self.delte_unused )
    
    pmc.menuItem( divider = True )
    
    pmc.menuItem( label = 'Connect Layers',
                  command = self.connect_layers )
    
    pmc.menuItem( label = 'Bake Selected layer',
                  command = self.do_bake_layer )
    
  
  def display_layers_menu( self, evt, smth):
    """
    Determines which layers menu elements are active and which are inactive.
    """
    pass
  
  def build_options_menu( self ):
    pmc.setParent( menu = True )
    
    menu = pmc.menu( label = 'Options', allowOptionBoxes = True )
    
    pmc.menuItem( label = 'Set xNormal Location',
                  command = self.set_xn_location )
    
    pmc.menuItem( divider = True )
    
    enable = utils.get_bake_normals( )
    if enable == None:
      utils.set_bake_normals( True )
      enable = True
    pmc.menuItem( label = 'Bake Normal Map',
                  cb = enable,
                  command = pmc.CallbackWithArgs( self.map_cbx_callback,
                                                  'normal' ) )
    enable = utils.get_bake_ao( )
    if enable == None:
      utils.set_bake_ao( False )
      enable = False
    pmc.menuItem( optionBox = True )
    pmc.menuItem( label = 'Bake Ambient Occlusion Map',
                  cb = enable,
                  command = pmc.CallbackWithArgs( self.map_cbx_callback,
                                                  'ao' ) )
    pmc.menuItem( optionBox = True )
  
  def build_help_menu( self ):
    pmc.setParent( menu = True )
    
    menu = pmc.menu( label = 'Help' )
  
  #==========================================================================
  # Event Handlers
  #==========================================================================
  
  # Layer Order
    
  def move_layer_up( self, evt ):
    """
    TODO: Add layer order functionality
    """
    pass
  
  def move_layer_down( self, evt ):
    """
    TODO: Add layer order functionality
    """
    pass
  
  # New Layer
  
  def new_empty( self, evt ):
    """
    Create a new empty bake layer
    Made a callback for this so I could refresh the UI
    """
    pmc.bakeLayer( )
    self.refresh()
  
  def new_selected( self, layer ):
    """
    Creat a new bake layer and add all selected objects to it
    """
    new_layer = pmc.bakeLayer( )
    utils.add_to_bake_layer( layer = new_layer )
    
    self.refresh()
  
  # Layer Members
  
  def add_objects( self, evt ):
    """
    Add objects to selected layer handler
    This only handles the call from the Layers menu at the top of the window.
    The call from the left click menu goes straight to the function
    in utils
    """
    for layer in self.get_selected_layers( ):
      utils.add_to_bake_layer( layer = layer )
  
  def select_objects( self, evt ):
    """
    Select the Maya objects that are members of the given layer.  This handles
    both the calls from the left click menu and the top menu
    """
    print evt
    objects = [ ]
    if evt == False:

      for layer in self.get_selected_layers( ):
        objects.extend( utils.get_members( layer ) )
    
    else:
      objects = utils.get_members( evt )
    pmc.select( objects )
  
  def remove_objects( self, evt ):
    """
    Add objects to selected layer handler
    This only handles the call from the Layers menu at the top of the window.
    The call from the left click menu goes straight to the function
    in utils
    """

    for layer in self.get_selected_layers( ):
      utils.remove_from_bake_layer( layer )
  
  # Remove Layers
  
  def delete_selected( self, layer ):
    """
    delete Bake Layers selected in the bake layer editor window.
    """
    pmc.delete( layer )
    self.refresh()

  def delte_unused( self, layer ):
    """
    Delete Bake Layers with no member objects
    """
    bake_layers = pmc.ls( typ = 'BakeLayer' )
    
    for layer in bake_layers:
      if len( utils.get_members( layer ) ) < 1:
        pmc.delete( layer )
        
    self.refresh( )
  
  # Edit Layers
  
  def connect_layers( self, evt ):
    """
    Connect two layers event handler.
    """
    high_layers = [ ]
    low_layers = [ ]
    
    for layer in self.get_selected_layers( ):
      if utils.is_high( layer ):
        high_layers.append( layer )
        
      else:
        low_layers.append( layer )

    if not len( low_layers ) == 1:
      pmc.error( 'Connecting Bake Layers requires one and only one low layer.' )
      return False

    utils.connect_layers( low_layers[ 0 ], high_layers )
  
  # Bake layer

  def do_bake_layer( self, layer ):
    """
    Bake the bake layer.  Gets some settings from the xml settings file saved
    in prefs, then passes them to the utils function
    """
    print layer
    utils.bake_layer( layer,
                                 bake_ao = utils.get_bake_ao( ),
                                 bake_normals = utils.get_bake_normals( ) )
    
  # Options
  
  def set_xn_location( self, evt ):
    """
    Set the location of xNormal on the user's hard drive
    """
    exe_filter = 'Applications (*.exe)'

    if not utils.get_xn_location( ) == None:
      xn_loc = pmc.fileDialog2( dialogStyle = 1,
                                cap = 'Locate xNormal.exe',
                                fileMode = 1,
                                fileFilter = exe_filter,
                                dir = utils.get_xn_location( ) )
    else:
      xn_loc = pmc.fileDialog2( dialogStyle = 1,
                                cap = 'Locate xNormal.exe',
                                fileMode = 1,
                                fileFilter = exe_filter )
 

    if not xn_loc == None:
      utils.set_xn_location( xn_loc[ 0 ] )
    
  def map_cbx_callback( self, map, evt ):
    """
    Callback for when user clicks on the "bake normal map" Check Box in the
    options menu
    """
    if map == 'normal':  
      utils.set_bake_normals( evt )
    elif map == 'ao':
      utils.set_bake_ao( evt )
    
  
  #============================================================================
  # Layer Editor button events
  #============================================================================
  
  def button_layer_select( self, item, state ):

    prev_selection = pmc.melGlobals[ 'selected_bake_layers' ]
    
    # Until I can figure out how to get shift/ctl detection working, this will
    # be only single selection

    pmc.treeView( self.__layer_tree,
                  e = True,
                  selectItem = ( item, state ) )
    
    selection = [ ]
      
    pmc.melGlobals[ 'selected_bake_layers' ] = selection
    
    self.refresh_button_state( )
    
  # After discovering treeView, not using this any more
  def button_quick_edit_window( self, layer, arg ):
    layer = utils.get_bake_layer( layer )
    
    quick_edit_window.EditBakeLayerWindow( self, layer )
  
  def button_layer_editor_rename( self, old_name, new_name ):
    node = utils.get_bake_layer( old_name )
    node.rename( new_name )
    
    self.refresh( )

  def button_type_change( self, layer, arg ):


    node = utils.get_bake_layer(layer)
    
    if utils.is_high( layer ):
      utils.set_low( layer )
    else:
      utils.set_high( layer )
      
    self.refresh( )
  
  def button_connection_edit( self, layer, arg ):
    
    selected_layer = pmc.treeView( self.__layer_tree,
                                   q = True,
                                   si = True )[ 0 ]
                                                              
    if utils.are_connected( layer, selected_layer ):
      utils.disconnect_layers( [ layer, selected_layer ] )
    else:
      if utils.is_high( selected_layer ):
        utils.connect_layers( layer, selected_layer )
      else:
        utils.connect_layers( selected_layer, layer )
    
    self.refresh_button_state()

  #============================================================================
  # Left click menu
  #============================================================================

  def show_left_click_menu( self, menu, layer ):
    if layer == '':
      return False
    pmc.setParent( menu, menu = True )
    
    if len( pmc.ls( sl = True ) ) < 1:
      selection = False
      
    else:
      selection = True
    
    is_high = utils.is_high( layer )
    
    if len( self.get_selected_layers( ) ) < 2:
      mult_select = False
    else:
      mult_select = True
   
    menu.deleteAllItems( )

    
    pmc.menuItem( label = layer + '...' )
   
    if not is_high:
      enable = True
    else:
      enable = False
      
    pmc.menuItem( label = 'Bake this layer',
                  enable = enable,
                  command = pmc.Callback( self.do_bake_layer,
                                          layer ) )
    pmc.menuItem( divider = True )
    
    if is_high:
      enable = False
    else:
      enable = True
      
    pmc.menuItem( label = 'Set layer to High-poly',
                  enable = enable,
                  command = pmc.Callback( utils.set_high,
                                          layer ) )
    
    if is_high:
      enable = True
    else:
      enable = False

    pmc.menuItem( label = 'Set layer to Low-poly',
                  enable = enable,
                  command = pmc.Callback( utils.set_low,
                                          layer ) )
    pmc.menuItem( divider = True )
    
    enable = mult_select
    
    pmc.menuItem( label = 'Connect Selected Layers',
                  enable = enable,
                  command = self.connect_layers )
    
    pmc.menuItem( divider = True )
    
    if not selection:
      enable = False
    else:
      enable = True
    
    pmc.menuItem( label = 'Add selected objects',
                  enable = enable,
                  command = pmc.Callback( utils.add_to_bake_layer,
                                          layer ) )
    
    pmc.menuItem( label = 'Remove selected objects',
                  enable = enable,
                  command = pmc.Callback( utils.remove_from_bake_layer,
                                          layer ) )
    
    pmc.menuItem( label = 'Select Objects',
                  command = pmc.Callback( self.select_objects,
                                          layer ) )
    
    pmc.menuItem( divider = True )
    
    pmc.menuItem( label = 'Delete',
                  command = pmc.Callback( self.delete_selected,
                                          layer ) )
    return True
  
  #============================================================================
  # Utilities
  #============================================================================

  def get_selected_layers( self ):
    selection = [ ]
    
    if  pmc.treeView( self.__layer_tree, q = True, si = True ) == None:
      return [ ]
    else:
      for item in pmc.treeView( self.__layer_tree, q = True, si = True ) :
        selection.append( utils.get_bake_layer( item ) )
        
    return selection

  def new_scene( self ):
    
    pmc.deleteUI( self.__window )
    
    #self.__window.delete() 
    
    #self.__layer_layout.clear( )
    #self.refresh( )
    #pmc.melGlobals[ 'selected_bake_layers' ] = [ ]
  
  def open_scene( self ):
    
    self.__window.delete( )
    
    #self.__layer_layout.clear( )
    #self.refresh( )
    #pmc.melGlobals[ 'selected_bake_layers' ] = [ ]

  
  def refresh( self ):

    bake_layers = pmc.ls( typ = 'BakeLayer' )
    
    for layer in bake_layers:
      pass

    # Build the new layout
    
    pmc.treeView( self.__layer_tree, e = True, removeAll = True )
    
    for layer in bake_layers:
      
      # Create Button
      if utils.is_high( layer ):
        h_l_button = 'H'
        low = False
        rd_button = False
      else:
        h_l_button = 'L'
        low = True
        rd_button = bake_layer_tool.get_image( 'ray_dist.png' )

      pmc.treeView( self.__layer_tree,
                    e = True,
                    addItem = ( layer.name( ), '' ) )
      
      pmc.treeView( self.__layer_tree,
                    e = True,
                    bti = ( layer.name( ), 1, h_l_button ) )
      
      
      pmc.treeView( self.__layer_tree,
                    e = True,
                    eb = ( layer, 3, low ),
                    i = ( layer, 3, rd_button ) )
      
      
      
    self.refresh_button_state()
      
        
  def refresh_button_state( self ):
    
    bake_layers = pmc.ls( typ = 'BakeLayer' )
    
    one_selected = False
    if pmc.treeView( self.__layer_tree, q = True, si = True ) == None:
      pass 
    elif len( pmc.treeView( self.__layer_tree, q = True, si = True ) ) == 1:
      one_selected = True
      sel_layer = pmc.treeView( self.__layer_tree, q = True, si = True )[ 0 ]
    
    connected_layers = [ ]
    
    if one_selected:
      selected_is_high = utils.is_high( sel_layer )
      if selected_is_high:
        connected_layers = utils.get_connected_low_layers( sel_layer )
      else:
        connected_layers = utils.get_connected_high_layers( sel_layer )
    

    for layer in bake_layers:
      
      if one_selected == True:
        if selected_is_high == utils.is_high( layer ):
          pmc.treeView( self.__layer_tree,
                        e = True,
                        eb = ( layer, 2, False ),
                        i = ( layer, 2, '' ) )
          
          
        
        else:
          if utils.get_bake_layer( layer ) in connected_layers:
            image = bake_layer_tool.get_image( 'link_icon.png' )
          else:
            image = bake_layer_tool.get_image( 'unlink_icon.png' )
  
            
          pmc.treeView( self.__layer_tree,
                        e = True,
                        eb = ( layer, 2, True ),
                        i = ( layer, 2, image ) )
      
      else:
        pmc.treeView( self.__layer_tree,
                      e = True,
                      eb = ( layer, 2, False ),
                      i = ( layer, 2, '' ) )
      

