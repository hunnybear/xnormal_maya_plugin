'''
Created on Jun 30, 2011

@author: Tyler
'''
HIGH = 'high'
LOW = 'low'

import pymel.core as pmc


import bake_layer_tools
import utils

reload( bake_layer_tools )
reload( utils )

class Widget( object ):
  '''
  the Abstract class that serves as a base class for the useful widgets
  '''
  
  def __init__( self, parent, *args, **kwargs ):
    
    self.parent = parent
    
    self.focused_element = None
    
    self.build( )
    
    self.refresh( ) 
    
  def build( self ):
    """
    placeholder method
    """
    pass
  
  def refresh( self ):
    """
    placeholder method
    """

class BakeSettingsWidget( Widget ):
  
  def build( self ):
    
    self.rows = [ ]
    
    self.bake_file_location = ''
    
    pmc.setParent( self.parent )
    
    self.rows.append( pmc.rowColumnLayout( numberOfColumns = 1 ) )
    
    self.file_button = pmc.textFieldButtonGrp( label = 'Bake to:',
                                               cw1 = 5,
                                               text = self.bake_file_location,
                                               buttonLabel = 'Browse',
                                               buttonCommand = self.handle_browse )
    
  def handle_browse( self ):
    
    tex_filter = 'Targa (*.tga)'
    
    self.bake_file_location = pmc.fileDialog2( dialogStyle = 1,
                                               cap = 'Set base file name',
                                               fileMode = 0,
                                               fileFilter = tex_filter )[ 0 ]
                                               
    pmc.confirmDialog( message = self.bake_file_location )
    
    
class ConfirmWidget( Widget ):
  
  def build( self ):
    
    self.high_objs = [ ]
    self.low_objs = [ ]
    
    self.row = pmc.rowColumnLayout( numberOfColumns = 3 )
    
    self.btn_clear = pmc.button( label = 'Clear All',
                                 command = self.handle_clear )
    
    self.btn_bake = pmc.button( label = 'Bake',
                                command = self.handle_bake )

    self.btn_cancel = pmc.button( label = 'Cancel',
                                  command = self.handle_cancel )
    

    
  def handle_bake( self, evt ):
    xn_settings = utils.XNConfigSettings( )
    
    # ToDO: make this cleaner
    bake_layers = self.parent.bake_layers.bake_layers
    
  def handle_clear( self, evt ):
    pass
  
  def handle_cancel( self, evt ):
    pass
    
    
class LayerBoxesWidget( Widget ):

  def build( self ):
    
    #self.parent.bake_layers = utils.
    self.focused_element = None
    
    self.rows = [ ]
    
    pmc.setParent( self.parent )
    
    self.rows.append( pmc.rowColumnLayout( numberOfColumns = 2 ) )
    
    self.low_box = pmc.textScrollList( numberOfRows = 10,
                                       allowMultiSelection = False,
                                       showIndexedItem = 1,
                                       selectCommand = pmc.Callback( self.handle_click,
                                                                     'low' ) )
    self.high_box = pmc.textScrollList( numberOfRows = 10,
                                        allowMultiSelection = True,
                                        showIndexedItem = 1,
                                        selectCommand = pmc.Callback( self.handle_click,
                                                                      'high' ) )
    
    self.list_boxes = [ self.low_box, self.high_box ]
    
  def handle_click( self, sel_list ):
    self.focused_element = sel_list
    self.refresh( )
    
    if not sel_list == 'low':
      self.low_box.deselectAll( )
      
    if not sel_list == 'high':
      self.high_box.deselectAll( )
      
  def refresh( self ):
    
    selected = [ ]
    
    for list_box in self.list_boxes:
      
      # Get all selected elements.
      
      list_sel = list_box.getSelectItem( )
      
      if not list_sel == None:
        for item in list_sel:
          selected.append( item )
          
      # Clear the textScrollLists
      
      list_box.removeAll( )
      
    for layer in pmc.ls( typ = 'BakeLayer' ):
      is_high = bake_layer_tools.is_high( layer )
      
      if not is_high:
        self.low_box.append( layer )
        
      else:
        self.high_box.append( layer )
    
    # Re-select layers
    for list_box in self.list_boxes:
      contained_layers = list_box.getAllItems( )
      
      try:
        for layer in contained_layers:
          if layer in selected:
            list_box.setSelectItem( layer )
      except TypeError:
        pass

class EditBakeLayerWindow( object ):
  
  def __init__( self, parent, layer ):
    self.parent = parent
    self.layer = bake_layer_tools.get_bake_layer( layer )
    
    self.__window = pmc.window( title = 'Edit Bake Layer' )
    
    self.build( )
    
    self.refresh( )
    
    self.__window.show( )
    
  def build( self ):
    
    form = pmc.formLayout( )
    pmc.setParent( form )
    is_high = bake_layer_tools.is_high( self.layer )
    
    body = pmc.columnLayout( rowSpacing = 4 )
    
    self.name_field = pmc.textFieldGrp( columnWidth = [ 1, 70 ],
                                   label = 'Name',
                                   text = self.layer.name( ),
                                   editable = True )
    
    self.high_low = pmc.radioButtonGrp( columnWidth = [ 1, 70 ],
                                   nrb = 2,
                                   l = 'Layer Type:',
                                   l1 = 'High-poly',
                                   l2 = 'Low-poly' )
    
    if is_high:
      self.high_low.setSelect( 1 )
    else:
      self.high_low.setSelect( 2 )
    
    button_form = pmc.formLayout( parent = form )

    
    btn_save = pmc.button( label = 'Save',
                           command = self.save_changes )
    
    btn_cancel = pmc.button( label = 'Cancel',
                             command = self.cancel_changes )
    
    
    button_form.attachForm( btn_save, 'top', 0 )
    button_form.attachForm( btn_save, 'left', 0 )
    button_form.attachForm( btn_save, 'bottom', 0 )
    button_form.attachPosition( btn_save, 'right',  2, 50 )
    
    button_form.attachForm( btn_cancel, 'top', 0 )
    button_form.attachPosition( btn_cancel, 'left', 2, 50 )
    button_form.attachForm( btn_cancel, 'bottom', 0 )
    button_form.attachForm( btn_cancel, 'right', 0 )
    
    form.attachForm( body, 'top', 4 )
    form.attachForm( body, 'left', 4 )
    #form.attachControl( body, 'bottom', 4, button_form )
    form.attachForm( body, 'right', 4 )
    
    form.attachNone( button_form, 'top' )
    form.attachForm( button_form, 'left', 4 )
    form.attachForm( button_form, 'bottom', 4)
    form.attachForm( button_form, 'right', 4 )
    
  def cancel_changes( self, evt ):
    pmc.deleteUI( self.__window )
    
  def save_changes( self, evt ):
    
    self.layer.rename( self.name_field.getText( ) )
    
    if self.high_low.getSelect( ) == 1:
      bake_layer_tools.set_high( self.layer )
    else:
      bake_layer_tools.set_low( self.layer )
    
    self.parent.refresh( )
    
    pmc.deleteUI( self.__window )
  
  def refresh( self ):
    pass
  
  
      
        