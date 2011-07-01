"""
Bake Layer Window main UI

Tyler Good 2011 tylergood@tylergood.net
"""

import pymel.core as pmc
import maya.OpenMaya as OpenMaya


import bake_layer_tools


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
    self.menu_dict = { }
    
    self.build( )
    
    self.refresh( )
    
    self.__window.show( )

  def build(self):
    self.build_menu_bar( )
    
    # Form layout for rest of window
    self.__form = pmc.formLayout( )
    
    # Buttons for quick access to things
    
    btn_move_layer_up = pmc.symbolButton( image = 'moveLayerUp.png',
                                          annotation = 'Move Layer up',
                                          command = self.move_layer_up )
    
    btn_move_layer_down = pmc.symbolButton( image = 'moveLayerDown.png',
                                            annotation = 'Move Layer down',
                                            command = self.move_layer_down )
    
    btn_new_empty_layer = pmc.symbolButton( image = 'newLayerEmpty.png',
                                            annotation = 'New Empty Bake Layer',
                                            command = self.new_empty )
    
    btn_new_selected_layer = pmc.symbolButton( image = 'newLayerSelected.png',
                                               annotation = 'New Bake Layer from Selection',
                                               command = self.new_selected )
    
    
    pmc.setParent( self.__form )
    
    self.__scroll_layout = pmc.scrollLayout( horizontalScrollBarThickness = 0,
                                             backgroundColor = [ 0.165, 0.165, 0.165 ],
                                             )
    
    self.__layer_layout = pmc.gridLayout( allowEmptyCells = False,
                                          autoGrow = True,
                                          numberOfColumns = 1,
                                          cellWidthHeight = [ 350, 20 ] )
    
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
    
    self.__form.attachControl( self.__scroll_layout, 'top', 1, btn_new_empty_layer )
    self.__form.attachForm( self.__scroll_layout, 'left', 0 )
    self.__form.attachForm( self.__scroll_layout, 'bottom', 0 )
    self.__form.attachForm( self.__scroll_layout, 'right', 0 )

  def refresh( self ):
    
    bake_layers = pmc.ls( typ = 'BakeLayer' )
    for i in bake_layers:
      print i
    
    # Get all layers previously in the layout
    
    layer_list = self.__layer_layout.children( )
    print layer_list
    
    # Check for selection 
    
    for layer in bake_layers:
      pass
    
    # Clear the old layout
    
    self.__layer_layout.clear( )

     
    
    # Build the new layout

    for layer in bake_layers:
      
      # Create Button
      layer_button = pmc.layerButton( parent = self.__layer_layout,
                                      label = layer.name( ),
                                      name = layer.name( ),
                                      width =  350,
                                      doubleClickCommand = self.button_quick_edit_window,
                                      renameCommand = self.button_layer_editor_rename )
      layer_button.command( pmc.Callback( self.button_layer_select, layer_button ) )
      
     
      # Left click menu
      
      left_click_menu = pmc.popupMenu( button = 3, parent = layer )
   
      left_click_menu.postMenuCommand( pmc.Callback( self.show_left_click_menu, 
                                                     layer_button,
                                                     left_click_menu ) )


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
    
    new_empty = pmc.menuItem( label = 'Create Empty Layer',
                              command = self.new_empty )
    self.menu_dict[ 'layers' ][ 'new_empty' ] = new_empty
    new_from_selection = pmc.menuItem( label = 'Create Layer from Selected',
                                       command = self.new_selected )
    
    pmc.menuItem( divider = True )
    
    select_objects = pmc.menuItem( label = 'Select Objects in Selected Layers',
                                   command = self.select_objects )
    remove_objects = pmc.menuItem( label = 'Remove Selected Objects from Selected Layers',
                                   command = self.remove_objects )

    pmc.menuItem( divider = True )

    delete_selected = pmc.menuItem( label = 'Delete Selected Layers',
                                    command = self.delete_selected )
    delete_unused = pmc.menuItem( label = 'Delete Unused Layers',
                                  command = self.delte_unused )
    
  
  def display_layers_menu( self, evt):
    """
    Determines which layers menu elements are active and which are inactive.
    """
    pass
  
  def build_options_menu( self ):
    pmc.setParent( menu = True )
    
    menu = pmc.menu( label = 'Options' )
  
  def build_help_menu( self ):
    pmc.setParent( menu = True )
    
    menu = pmc.menu( label = 'Help' )
  
  #==========================================================================
  # Event Handlers
  #==========================================================================
  
  # Layer Order
    
  def move_layer_up( self, evt ):
    pass
  
  def move_layer_down( self, evt ):
    pass
  
  # New Layer
  
  def new_empty( self, evt ):
    pass
  
  def new_selected( self, evt ):
    pass
  
  # Layer Members
  
  def add_objects( self, evt ):
    bake_layer_tools
  
  def select_objects( self, evt ):
    pass
  
  def remove_objects( self, evt ):
    pass
  
  # Remove Layers
  
  def delete_selected( self, evt ):
    pass
  
  def delte_unused( self, evt ):
    pass
  
  #============================================================================
  # Layer Editor button events
  #============================================================================
  
  def button_layer_select( self, button ):

    prev_selection = pmc.melGlobals[ 'selected_bake_layers' ]
    
    # Until I can figure out how to get shift/ctl detection working, this will
    # be only single selection
    print button.getSelect()
    button.setSelect( True )
    
  
  def button_quick_edit_window( self, evt ):
    pass
  
  def button_layer_editor_rename( self, evt ):
    pass

  #============================================================================
  # Left click menu
  #============================================================================

  def show_left_click_menu( self, button, menu ):
    pmc.setParent( menu, menu = True )
    
   
    menu.deleteAllItems( )

    
    pmc.menuItem( label = button.shortName( ) + '...' )
    pmc.menuItem( divider = True )
    
    pmc.menuItem( label = 'Add selected objects',
                  command = self.add_objects )
    
    pmc.menuItem( label = 'Remove selected objects',
                  command = self.remove_objects )
    
    pmc.menuItem( label = 'Select Objects',
                  command = self.select_objects )

  #============================================================================
  # Window for editing attributes of layer
  #============================================================================
  
  def quick_edit_window( self ):
    pass

