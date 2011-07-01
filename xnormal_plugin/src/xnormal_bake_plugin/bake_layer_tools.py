'''
Created on Jun 30, 2011

@author: Tyler
'''

HIGH_CONNECT_ATTR = 'hc'
LOW_CONNECT_ATTR = 'lc'

import pymel.core as pmc

import maya.OpenMaya as OpenMaya

print_info = OpenMaya.MGlobal.displayInfo
print_warning = OpenMaya.MGlobal.displayWarning
print_error = OpenMaya.MGlobal.displayError

#==============================================================================
# new Bake Layers
#==============================================================================

def create_bake_layer( name = None,
                       type='low',
                       dialog = False ):
  pass

def create_bake_layer_from_selection( name = None,
                                      type = 'low',
                                      dialog = False ):
  pass

#==============================================================================
# Layer Members
#==============================================================================

def select_from_bake_layer( layer ):
  
  node = get_bake_layer( layer )
  
  if node == None:
    raise Exception( 'select_from_bake_layer requires one "BakeLayer" node.')
    

def remove_from_bake_layer( layer, objects = None ):
  pass

def add_to_bake_layer( layer = None, l = None, objects = None, o = None ):
  
  # Take care of alternate kwargs
  
  if objects == None:
    objects = o   
  if layer == None:
    layer = l
  
  # Get the node for the bake Layer  
  
  layer_node = get_bake_layer( layer )
  if layer_node == None:
    raise Exception( 'add_to_bake_layer requires one "BakeLayer" node.')
  
  # get the list of nodes for the objects
  
  if isinstance( objects, pmc.nt.Transform ):
    obj_list = [ objects ]
  
  elif isinstance( pmc.PyNode( objects ), pmc.nt.Transform ):
    obj_list = [ pmc.PyNode( objects ) ]
    
  elif isinstance( object, [ tuple, list ] ):
    obj_list = objects
    
  else:
    obj_list = pmc.ls( sl = True, typ = 'Transform' )
  
  # Make connections
    
  for obj in obj_list:
    
    multi_connect(layer_node, 'lm', obj, 'bake')

#==============================================================================
# Edit Layer
#==============================================================================
    
def set_high( layer ):
  layer_node = get_bake_layer( layer )
  
  layer_node.setAttr( 'hp', True )
  
def set_low( layer ):
  layer_node = get_bake_layer( layer )
  
  layer_node.setAttr( 'hp', False )
  
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
  
  for lay in high_layers:
    
    multi_connect(low_layer, HIGH_CONNECT_ATTR, lay, LOW_CONNECT_ATTR )
  
    
def disconnect_layers( layers ):
  layer_nodes = [ ]
  for layer in layers:
    node = get_bake_layer( layer )
    if not node == False:
      layer_nodes.append( node )
        
  for layer in layer_nodes:
    connect_attr = layer.attr( HIGH_CONNECT_ATTR )
    for high_layer in get_connected_high_layers( layer ) :
      if high_layer in layer_nodes:
        for high_attr in high_layer.listAttr( ):
          if high_attr.attrName( )[ : len( LOW_CONNECT_ATTR )] == LOW_CONNECT_ATTR:
            conn = high_attr.listConnections( plugs = True )
            if connect_attr in conn:
              pmc.disconnectAttr( connect_attr, high_attr )
      
#==============================================================================
# Query Layer
#==============================================================================
    
def is_high( layer ):
  layer_node = get_bake_layer(layer)

  return layer_node.getAttr( 'hp' )

def get_connected_low_layers( layer ):
  
  node = get_bake_layer(layer)
  
  low_layers = [ ]
  
  if node == False:
    raise Exception( 'get_connected_low_layers requires one Bake Layer node.' )
  
  for attr in node.listAttr( ):
    print attr.name( )[ : len( LOW_CONNECT_ATTR )]
    if( attr.name( )[ : len( LOW_CONNECT_ATTR )] == LOW_CONNECT_ATTR and
        attr.isDestination( ) and
        isinstance( attr.inputs( )[ 0 ], pmc.nt.BakeLayer ) ) :
      low_layers.append( attr.inputs( )[ 0 ] )
      
  return low_layers
      
def get_connected_high_layers( layer ):
  
  node = get_bake_layer( layer )
  
  high_layers = [ ]
  
  if node == False:
    raise Exception( 'get_connected_high_layers requires one Bake Layer node.' )
      
  conn_attr = layer.attr( HIGH_CONNECT_ATTR )
  
  for obj in conn_attr.listConnections( ):
    if isinstance(obj, pmc.nt.BakeLayer ):
      high_layers.append( obj )
      
  return high_layers
    
#==============================================================================
# Helper Functions
#==============================================================================

def disconnect_nodes( nodes ):
  for node in nodes:
    for attr in node.listAttr( ):
      for conn in attr.listConnections( ):
        if conn in nodes:
          for conn_attr in conn.listAttr( ):
            if conn_attr.isConnectedTo( attr ):
              pass
              
      
      

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