import pymel.core as pmc
import os

# Meta Data
from tool_info import TOOL_NAME
from tool_info import VERSION_NUMBER
from tool_info import SUITE_NAME
MAIN_DIR = os.path.normpath( os.path.dirname( __file__ ) )
IMAGES_DIR = os.path.normpath( os.path.join( MAIN_DIR, 'images' ) ).replace( '\\', '/' )
PLUGIN_DIR = os.path.normpath( os.path.join( MAIN_DIR, 'plugins' ) ).replace( '\\', '/' )
SHELF_NAME = SUITE_NAME

def init( ):
  pass

def create_shelf( ):
  pass

def load_plugin( auto_load = False ):
  add_plugin_dir( )
  plugin_file = os.path.normpath( '{0}/bake_layer_init.py'.format( PLUGIN_DIR ) )
  if not pmc.pluginInfo( 'bake_layer_init.py', q = True, loaded = True ):
    pmc.loadPlugin( plugin_file )
    
#==============================================================================
# Utilities
#==============================================================================

def add_plugin_dir( ):
  if os.environ.has_key( 'MAYA_PLUG_IN_PATH' ):
    if not PLUGIN_DIR in os.environ[ 'MAYA_PLUG_IN_PATH' ]:
      os.environ[ 'MAYA_PLUG_IN_PATH' ] += ';{0}'.format( PLUGIN_DIR )
#==============================================================================
#  Shelf-related
#==============================================================================
def __clear_shelf_tab( shelf_name ):
  shelf = __get_shelf_layout( shelf_name )
  
  buttons = pmc.shelfLayout( shelf, q = True, ca = True )
  if not buttons == None:
    for button in buttons:
      pmc.deleteUI( button )
      
  return shelf

def __get_shelf_layout( shelf_name ):
  """
  Returns path to layout of a shelf
  """
  if __shelf_exists( shelf_name ):
    shelf = '{0}|{1}'.format( __get_main_shelf( ), shelf_name )
    return shelf
  else:
    return None
  
def __create_shelf( ):
  """
  Create shelf for tools made by Tyler Good
  """
  
  shelf = SHELF_NAME
  if pmc.shelfLayout( shelf, q = True, exists = True ):
    pmc.shelfLayout( shelf, )
    
    
def __get_main_shelf( ):
  """
  Return paht to main shelfTabLayout
  """
  
  main_shelf = pmc.melGlobals[ 'gShelfTopLevel' ]
  if pmc.shelfTabLayout( main_shelf, ex = True ):
    return main_shelf
  
  else:
    return None
  
def __shelf_exists( shelf_name ):
  """
  Return True if a shelf Exists, False if it does not
  """
  
  exists = False
  
  main_shelf = __get_main_shelf( )
  if main_shelf is None:
    return False
  
  tabs = pmc.shelfTabLayout( main_shelf, q = True, ca = True )
  if not tabs is None:
    exists = ( shelf_name in tabs )
    
  return exists