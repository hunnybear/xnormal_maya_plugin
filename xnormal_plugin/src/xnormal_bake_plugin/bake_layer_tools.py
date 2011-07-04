'''
Created on Jun 30, 2011

@author: Tyler
'''

import os
import subprocess

import pymel.core as pmc
import maya.cmds as mc

import maya.OpenMaya as OpenMaya

import utils
reload( utils )

from xnormal_bake_plugin.tool_info import TOOL_NAME
from xnormal_bake_plugin.tool_info import VERSION_NUMBER

print_info = OpenMaya.MGlobal.displayInfo
print_warning = OpenMaya.MGlobal.displayWarning
print_error = OpenMaya.MGlobal.displayError

HIGH_CONNECT_ATTR = 'hc'
LOW_CONNECT_ATTR = 'lc'
LAYER_MEMBERS_ATTR = 'lm'

#==============================================================================
# Layer Members
#==============================================================================

def select_from_bake_layer( layer ):
  
  node = get_bake_layer( layer )
  
  if node == None:
    print_error( 'select_from_bake_layer requires one "BakeLayer" node.')
    

def remove_from_bake_layer( layer, objects = None ):
  if objects == None:
    objects = pmc.ls( sl = True )

  node = get_bake_layer( layer )
  if node == False:
    pmc.error( 'You must specify a Bake Layer for this command' )
    return False
      
  connect_attr = node.attr( LAYER_MEMBERS_ATTR )
  

  for plug in pmc.connectionInfo( connect_attr, destinationFromSource = True ):
    if pmc.PyNode( plug.split( '.' )[ 0 ] ) in objects:
    
      pmc.disconnectAttr( connect_attr, plug )

def add_to_bake_layer( layer = None, objects = None ):

  
  # Get the node for the bake Layer  
  
  layer_node = get_bake_layer( layer )
  if layer_node == None:
    print_error( 'add_to_bake_layer requires one "BakeLayer" node.')
  
  # get the list of nodes for the objects
  
  if objects == None:
    print_info( 'No objects specified, using selection' )
    obj_list = pmc.ls( sl = True, typ = 'transform' ) 
  
  elif isinstance( objects, pmc.nt.Transform ):
    obj_list = [ objects ]
  
  elif isinstance( pmc.PyNode( objects ), pmc.nt.Transform ):
    obj_list = [ pmc.PyNode( objects ) ]
    
  elif isinstance( object, [ tuple, list ] ):
    obj_list = objects
    
  else:
    print_error( 'Objects supplied for add_to_bake_layer command were invalid' )

  if len( obj_list ) < 1:
    print_error( 'No valid objects were supplied or selected for the bake_layer_command' )
  
  # Make connections
    
  for obj in obj_list:
    
    multi_connect(layer_node, 'lm', obj, 'bake')
    
def get_members( layer ):
  layer_node = get_bake_layer(layer)
  
  return layer_node.attr( LAYER_MEMBERS_ATTR ).listConnections( )
  
  

#==============================================================================
# Edit Layer
#==============================================================================
    
def set_high( layer ):
  layer_node = get_bake_layer( layer )

  layer_node.setAttr( 'hp', True )
  
  layer_node.attr( HIGH_CONNECT_ATTR ).disconnect( )
  
def set_low( layer ):
  layer_node = get_bake_layer( layer )

  layer_node.setAttr( 'hp', False )
  
  for attr in layer_node.listAttr( ):
    if attr.name( )[ :len( LOW_CONNECT_ATTR ) ] == LOW_CONNECT_ATTR:
      attr.disconnect( )
      attr.delete( )
  
def connect_layers( low, high ):
  
  # Check low-poly layer
  low_layer = get_bake_layer ( low )
  if low_layer == None or is_high( low_layer ):
    raise Exception( 'connect_layers requires one low-poly Bake Layer be specified.' )

  high_layers = [ ]

  # Handle lists of high poly layers
  if isinstance(high, ( tuple, list ) ):
    
    
    for lay in high:
      hl = get_bake_layer( lay )
      
      if not hl == False:
        high_layers.append( hl )
  
  # Handle single high poly layers
  else:
    hl = get_bake_layer( high )
    
    if not hl == None:
      if is_high( hl ):
        high_layers.append( hl )
      
  if len( high_layers ) < 1:
    raise Exception( 'connect_layers requires at least one high-poly Bake Layer be specified.' )
  
  connected_high_layers = get_connected_high_layers( low_layer )
  
  for lay in high_layers:
    
    if lay not in connected_high_layers:
      multi_connect(low_layer, HIGH_CONNECT_ATTR, lay, LOW_CONNECT_ATTR )
  
    
def disconnect_layers( layers ):
  layer_nodes = [ ]
  for layer in layers:
    node = get_bake_layer( layer )
    if not node == False:
      layer_nodes.append( node )
        
  for layer in layer_nodes:
    connect_attr = layer.attr( HIGH_CONNECT_ATTR )
    

    for plug in pmc.connectionInfo( connect_attr, destinationFromSource = True ):
      if pmc.PyNode( plug.split( '.' )[ 0 ] ) in layer_nodes:
      
        pmc.disconnectAttr( connect_attr, plug )
      
#==============================================================================
# Query Layer
#==============================================================================

def are_connected( layer1, layer2 ):
  
  node1 = get_bake_layer( layer1 )
  node2 = get_bake_layer( layer2 )
  
  if is_high( node1 ):
    if node2 in get_connected_low_layers( node1 ):
      return True
    
  else:
    if node2 in get_connected_high_layers( node1 ):
      return True
  
  return False    
  
def is_high( layer ):
  layer_node = get_bake_layer(layer)

  return layer_node.getAttr( 'hp' )

def get_connected_low_layers( layer ):
  
  node = get_bake_layer(layer)
  
  low_layers = [ ]
  
  if node == False:
    raise Exception( 'get_connected_low_layers requires one Bake Layer node.' )
  
  for attr in node.listAttr( ):
    attr_name = attr.name( ).split( '.' )[ 1 ]
    if( attr_name[ : len( LOW_CONNECT_ATTR )] == LOW_CONNECT_ATTR and
        attr.isDestination( ) and
        isinstance( attr.inputs( )[ 0 ], pmc.nt.BakeLayer ) ) :     
      low_layers.append( attr.inputs( )[ 0 ] )
      
  return low_layers
      
def get_connected_high_layers( layer ):
  
  node = get_bake_layer( layer )
  
  high_layers = [ ]
  
  if node == False:
    raise Exception( 'get_connected_high_layers requires one Bake Layer node.' )
      
  conn_attr = node.attr( HIGH_CONNECT_ATTR )
  
  for obj in conn_attr.listConnections( ):
    if isinstance(obj, pmc.nt.BakeLayer ):
      high_layers.append( obj )
      
  return high_layers
    
#==============================================================================
# Baking and Export
#==============================================================================
    
def export_layer( layer ):
  
  layer_node = get_bake_layer( layer )
  members = get_members( layer_node )
  
  pmc.select( clear = True )
  
  meshes = [ ]
  
  project_dir =  pmc.workspace.getPath( )
  data_dir = project_dir + r'/xn_bake_data'
  
  if not os.path.exists( data_dir ):
    os.mkdir( data_dir )
    
  if not members == None:
    for orig_obj in members:
      
      new_obj = pmc.duplicate( orig_obj )[ 0 ]
      
      pmc.delete( new_obj, constructionHistory = True )
      
      relatives = new_obj.listRelatives( )
      
      for r in relatives:
        if r.nodeType( ) == 'mesh':
          
          meshes.append( new_obj )
          
  bake_mesh = make_bake_mesh( meshes )
  
  if not os.path.exists( data_dir + r'/xnezbake/' ):
    os.mkdir( data_dir + r'/xnezbake/' )
    
  pmc.select( bake_mesh )
  
  # Check that OBJ Export is enabled
  if not pmc.pluginInfo( 'objExport.mll', q = True, loaded = True ):
    pmc.loadPlugin( 'objExport.mll' )
  
  output = pmc.exportSelected( data_dir + r'/xnezbake/' + layer_node.name( ) + '.obj',
                               force = True,
                               options = 'groups=0;ptgroups=0;materials=0;smoothing=1;normals=1',
                               type = 'OBJexport' )
  
  pmc.delete( )

  return output

def get_base_export_file( layer ):
  
  layer_node = get_bake_layer(layer )
  
  project_dir =  pmc.workspace.getPath( )
  data_dir = project_dir + '/xn_bake_data'
  
  if not os.path.exists( data_dir + r'/xnezbake/' ):
    os.mkdir( data_dir + r'/xnezbake/' )
    
  return data_dir + r'/xnezbake/' + layer_node.name( ) + '.tga'

def make_bake_mesh( meshes, name = '' ):
  """
  Turn one or more meshes into a single mesh for export to xNormal
  """
  
  arg_string = ''
  meshes = list( set( meshes ) )
  
  pmc.select( clear = True )
  
  if len( meshes ) > 1:

    if name == '':
      name = 'bake_mesh'
      
    merged = pmc.polyUnite( meshes, ch = False, name = name )
    
  else:
    merged = meshes[ 0 ]
    
  tr = pmc.polyTriangulate( merged, ch = False)
  
  return merged

def bake_layer( low_layer,
                bake_ao = False,
                bake_normals = False ):
  
  # Layer/obj Related Vars
  
  low_node = get_bake_layer( low_layer )
  low_export = export_layer( low_node )
  
  base_file = get_base_export_file( low_node )
  
  high_exports = [ ]
  
  # xNormal related vars
  xn_loc = utils.get_xn_location( )
  if xn_loc == None:
    pmc.error( 'No location for xNormal has been set' )
    return False
  
  for high in get_connected_high_layers( low_node ):
    high_exports.append( export_layer( high ) )
    
  # The XML DOM object
  config = utils.XNConfigSettings( )
  
  # xml settings file for xNormal
  xml_path = config.file_path
  
  # set up the XML file for baking
  config.set_bake_meshes( [ low_export ], high_exports ) 
  config.set_base_file( base_file )
  
  # Tell Xn which maps to bake
  config.bake_ao( bake_ao )
  config.bake_normals( bake_normals )

  args = eval( '[ r"' + xn_loc + '", r"' + xml_path + '" ]' ) 

  # Ship it!
  subprocess.Popen( args )
    
#==============================================================================
# Helper Functions
#==============================================================================

def multi_connect( out_node, out_attr_name,
                   in_node, in_attr_name ):
  
  # TODO: prevent connection if connection already exists
  
  i = 0
  in_plug = None
  
  while in_plug == None:
    
    curr_attr = in_attr_name + str( i )
    
    if not in_node.hasAttr( curr_attr ):
      
      in_plug = in_node.addAttr( curr_attr,
                                 at = 'bool' )
      
      
    else:
      if in_node.attr( curr_attr ).isDestination( ):
        i = i + 1
      
      else:
        in_plug = in_node.attr( curr_attr )
        
  out_plug = out_node.attr( out_attr_name )
  
  out_plug.connect( in_plug )
      
     

def get_bake_layer( layer ):
  
  if isinstance( layer, pmc.nt.BakeLayer ):
    return layer
  
  elif isinstance( pmc.PyNode( layer ), pmc.nt.BakeLayer ):
    return pmc.PyNode( layer )
  
  else:
    return None