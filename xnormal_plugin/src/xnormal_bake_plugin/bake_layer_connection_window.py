'''
Created on Jul 2, 2011

@author: Tyler
'''

import pymel.core as pmc

import widgets
reload( widgets )

from xnormal_bake_plugin.tool_info import TOOL_NAME
from xnormal_bake_plugin.tool_info import VERSION_NUMBER

class BakeLayerConnecitonEditor( object ):
  
  WINDOW_TITLE = 'Bake Layer Relationship Editor'
    
  
  def __init__( self, layer = None ):
    
    
    #if pmc.window( self.WINDOW_TITLE, exists = True ):
    #  pmc.deleteUI( self.WINDOW_NAME )
    
    self.__window = pmc.window( title = self.WINDOW_TITLE )
    
    self.build( )
    
    self.__window.show( )
    
  def build( self ):
    
    self.build_menu_bar( )
    
    self.main_col = pmc.columnLayout( )
    
    self.settings_widget = widgets.BakeSettingsWidget( self.main_col )
    self.layer_lists_widget = widgets.LayerBoxesWidget( self.main_col )
    self.confirm_widget = widgets.ConfirmWidget( self.main_col )
    
  def build_menu_bar( self ):
    self.__menu_bar = pmc.menuBarLayout( )
      
    # Build the individual menus
    self.build_layers_menu( )
    #self.build_options_menu( ) ## Not implementing this for a while
    # self.build_help_menu( ) ## Not implementing this for a while
  
  def build_layers_menu( self ):
    pmc.setParent( menu = True )
    
    menu = pmc.menu( label = 'Layers', allowOptionBoxes = True )
    
    