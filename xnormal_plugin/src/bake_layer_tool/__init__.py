'''
    tgood_xn_exporter
    0.5
    
    copyright (c) 2010 Tyler Good
    This is free software: free as in free speech, and free as in free beer.
    
    This file is __init__.py
    This Package is bake_layer_tool

    bake_layer_tool is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    bake_layer_tool is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with bake_layer_tool.  If not, see <http://www.gnu.org/licenses/>.
    
    Description:
        script created by Tyler Good for running xnormal straight from maya
        and baking maps

    please email me if you have any questions, comments, critques, or requests
    tyler@tylergood.net
    
'''
import pymel.core as pmc
import os

# Meta Data
SUITE_NAME = 'GoodUtils'
TOOL_NAME = 'EZXBake'
VERSION_NUMBER = '0.2.1'
AUTHOR_EMAIL = 'tyler@tylergood.net'

MAIN_DIR = os.path.normpath( os.path.dirname( __file__ ) )
IMAGES_DIR = os.path.normpath( os.path.join( MAIN_DIR, 'images' ) ).replace( '\\', '/' )
PLUGIN_DIR = os.path.normpath( os.path.join( MAIN_DIR, 'plugins' ) ).replace( '\\', '/' )
SHELF_NAME = SUITE_NAME

def setup( ):
  init( )
  add_to_env( env_command )
  
def init( ):
  load_plugin( True )
  create_shelf( tools )

def reinit( ):
  rebuild_shelf( SHELF_NAME, tools )

def add_to_env( text ):
  setup_path = os.path.normpath( os.path.join( MAIN_DIR, '..', 'userSetup.py') )
  if os.path.exists( setup_path ):
    print( 'path_exists' )
    f = open( setup_path, 'r' )
    # Line number
    ln = 0
    
    lines = f.readlines( )
    
    for line in range( len( lines ) ):
      if lines[ line ] == text[ 0 ]:
        matches = True
        for next in range( len ( text ) ):
          if not lines[ line + next ] == text[ next ]:
            matches = False
        # If we've found a match, return true
        if matches == True:
          return True
        
    new_file = f.read( )
    for line in text:
      new_file += '{0}\n'.format( line )
    
    f.close( )
    f = open( setup_path, 'w')
    f.write( new_file )
    
  else:
    f = open( setup_path, 'w' )
    new_file = ''
    for line in text:
      new_file += '{0}\n'.format( line )  

def load_plugin( auto_load = False ):
  add_plugin_dir( )
  plugin_file = os.path.normpath( '{0}/bake_layer_init.py'.format( PLUGIN_DIR ) )
  if not pmc.pluginInfo( 'bake_layer_init.py', q = True, loaded = True ):
    pmc.loadPlugin( plugin_file )
    
  if auto_load:
    pmc.pluginInfo( 'bake_layer_init.py', e = True, autoload = True )
    
#==============================================================================
# Utilities
#==============================================================================

def get_image( image ):
  full_image = os.path.normpath(os.path.join( IMAGES_DIR , image ) )
  return full_image

def add_plugin_dir( ):
  if os.environ.has_key( 'MAYA_PLUG_IN_PATH' ):
    if not PLUGIN_DIR in os.environ[ 'MAYA_PLUG_IN_PATH' ]:
      os.environ[ 'MAYA_PLUG_IN_PATH' ] += ';{0}'.format( PLUGIN_DIR )
#==============================================================================
#  Shelf-related
#==============================================================================

def create_shelf( tools ):
  shelf = SHELF_NAME
  if not __shelf_exists( shelf ):
    create_shelf_tab( shelf )
  build_shelf( shelf, tools )
  __select_shelf( shelf )

def rebuild_shelf( shelf, tools ):
  if __shelf_exists( shelf ):
    __clear_shelf_tab( shelf )
    build_shelf( shelf, tools )
    __select_shelf( shelf )

def create_shelf_tab( shelf_name ):
  if not __shelf_exists( shelf_name ):
    pmc.mel.addNewShelfTab( shelf_name )

def build_shelf( shelf_name, tools ):
  for tool in tools:
    if not __shelf_button_exists( shelf_name, tool[ 'name'] ):
      pmc.shelfButton( c = tool['command'],
                       i = tool['image'],
                       l = tool['name'],
                       stp = tool['sourceType'],
                       p = shelf_name )

def __clear_shelf_tab( shelf_name ):
  shelf = __get_shelf_layout( shelf_name )
  
  buttons = pmc.shelfLayout( shelf_name, q = True, ca = True )
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
  try:
    main_shelf = pmc.melGlobals[ 'gShelfTopLevel' ]
  except KeyError:
    return None
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

def __shelf_button_exists( shelf_name, button_name ):
    
    exists = False
    
    main_shelf = __get_main_shelf( )
    if main_shelf is None:
      return False
    
    tabs = pmc.shelfTabLayout( main_shelf, q = True, ca = True )
    if not tabs is None:
      __select_shelf( shelf_name )
      full_shelf = '{0}|{1}'.format( main_shelf, shelf_name )
      buttons = pmc.shelfLayout( full_shelf, q = True, ca = True )
      for button in buttons:
        full_button = '{0}|{1}'.format( full_shelf, button )
        if button_name == pmc.shelfButton( full_button, q = True, l = True ):
          return True


def __select_shelf( shelf_name ):
  """
  Makes a shelf the active shelf.
  """

  if __shelf_exists( shelf_name ):
    main_shelf = __get_main_shelf( )
    pmc.shelfTabLayout( main_shelf, e = True, st = shelf_name )

#==============================================================================
# Data for install
#==============================================================================

tools = [ { 'name' : 'Bake Layer Editor',
            'command' : 'import bake_layer_tool.bake_layer_window\nbake_layer_tool.bake_layer_window.BakeLayerWindow( )',
            'image' : get_image( 'ble_icon.png' ),
            'sourceType' : 'python' } ]

env_command = [ 'import {0}'.format( __name__ ),
                '{0}.init( )'.format( __name__ ) ]
