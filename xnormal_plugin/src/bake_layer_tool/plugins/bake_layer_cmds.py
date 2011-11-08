'''
    tgood_xn_exporter
    0.5
    
    copyright (c) 2010 Tyler Good
    This is free software: free as in free speech, and free as in free beer.
    
    This file is bake_layer_cmds.py
    This Package is bake_layer_tool.plugins

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

import re

# Maya imports
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya

# Tool imports
import bake_layer_node



#Because I'm lazy
print_info = OpenMaya.MGlobal.displayInfo
print_warning = OpenMaya.MGlobal.displayWarning
print_error = OpenMaya.MGlobal.displayError

# -----------------------------------------------------------------------------
# Command Definitions
# -----------------------------------------------------------------------------

class BakeLayerCmdBase( OpenMayaMPx.MPxCommand ):
  """
  Base class, so I can avoid typing some things multiple times
  """
  def add_conn_attribute( self, dep_node_fn, attr_name, attr_namelong ):
    # Used to add number to name of attribute
    i = 0
    
    # Used for while loop
    connection_found = False
    
    
    while not connection_found == True:
      # Set names of attrs
      current_attr = attr_name + str( i )
      current_attrlong = attr_namelong + str( i )
      
      # Check if current attr exists
      try:
        has_attr = dep_node_fn.hasAttribute( current_attr )
      except:
        has_attr = False
        
      # If current attr does not exist, create it, it is the one to use
      if not has_attr:
        num_attr = OpenMaya.MFnNumericAttribute( )

        connect_attr = num_attr.create(
                                       current_attrlong,
                                       current_attr,
                                       OpenMaya.MFnNumericData.kBoolean
                                       )
        
        
        dep_node_fn.addAttribute( connect_attr )
        
        return current_attr
      
      # If current attr does exist, check if it is connected
      else:
        plug = OpenMaya.MPlug( )
        
        plug = dep_node_fn.findPlug( current_attr, True )
        # If it is not connected, use current plug
        if not plug.isConnected():
          return current_attr
        # Otherwise, increment by one and continue
        i = i + 1

  def multi_connect( self, out_node, out_attr,
                     in_node, in_attr_name, in_attr_long ):
    """
    Inputs:
      out_node: MObject node
      out_attr_name: string
      in_node: MObject node
      in_attr_name: string
      in_attr_long: string
    """
    in_node_fn = OpenMaya.MFnDependencyNode( )
    in_node_fn.setObject( in_node )
    
    out_node_fn = OpenMaya.MFnDependencyNode( )
    out_node_fn.setObject( out_node )
    
    
    in_attr = self.add_conn_attribute( in_node_fn,
                                       in_attr_name,
                                       in_attr_long )
    
    fn_dg_modify = OpenMaya.MDGModifier( )

    fn_dg_modify.commandToExecute( 'connectAttr {0}.{1} {2}.{3}'.format(
                                       out_node_fn.name( ),
                                       out_attr,
                                       in_node_fn.name( ),
                                       in_attr ) )
    
    fn_dg_modify.doIt()

class BakeLayerCmd( BakeLayerCmdBase ):
  """
  A command to quickly create, edit, or query a bake_layer node
  """

  # Name of the command
  COMMAND_NAME = 'bakeLayer'
  
  #---
  # Flags
  #---
  
  # Name for the new node ( CEQ )
  NAME_FLAG = '-n'
  NAME_FLAG_LONG = '-name'
  
  # Whether the layer is a high layer or not ( CEQ )
  HIGH_FLAG = '-h'
  HIGH_FLAG_LONG = '-high_layer'
  
  def __init__( self ):
    OpenMayaMPx.MPxCommand.__init__( self )
    
    # Set attributes for the command.
    self.__is_query_used = False
    self.__is_edit_used = False
    self.__objects_to_add = OpenMaya.MSelectionList( )
    
    # Used for dependency node functions for this node
    self.__this_node_fn = OpenMaya.MFnDependencyNode( )
    
    # The name applied to the node
    self.__name_arg = '' 
    
  def doIt(self, args):
    
    #---
    # parse arguments
    #---
    
    # Get the argument data
    # If this fails, it raises its own exception
    try: arg_data = OpenMaya.MArgDatabase( self.syntax( ), args)
    except:
      pass
    
    else:
      
      # Name flag
      if not( arg_data.isEdit( ) or arg_data.isQuery( ) ):
        if arg_data.isFlagSet( self.NAME_FLAG ):
          self.__name_arg = arg_data.flagArgumentString( self.NAME_FLAG, 0 )
          
          # Individual checks for name correctness
          __not_null = not len( self.__name_arg ) < 1
          __alpha_first = self.__name_arg[ 0 ].isalpha( )
          __contiguous = len( re.split( '\W+', self.__name_arg ) ) <= 1
          
          # Raise exception if name is not valid
          if not ( __not_null and __alpha_first and __contiguous ):
            raise Exception( '{0} is not a valid node name'.format( self.__name_arg ) )
      
      elif arg_data.isQuery( ):
        cmd_objects = OpenMaya.MSelectionList( )
        arg_data.getObjects( cmd_objects )
        if not cmd_objects.length( ) == 1:
          raise Exception( 'calling {0} in query mode requires specifying one object'.format( self.COMMAND_NAME ) )
        else:
          iter = OpenMaya.MItSelectionList( cmd_objects, bake_layer_node.BakeLayer.PLUGIN_NODE_ID )
          
          self.doItQuery( )
      
      else:
        cmd_objects = OpenMaya.MSelectionList( )
        arg_data.getObjects( cmd_objects )
        if cmd_objects.length( ) < 1:
          raise Exception( 'calling {0} in edit mode requires specifying at least one object'.format( self.COMMAND_NAME ) )
        else:
          iter = OpenMaya.MItSelectionList( cmd_objects, bake_layer_node.BakeLayer.PLUGIN_NODE_ID )
          
             
        
      self.__isEditUsed = arg_data.isEdit( )
      self.__isQueryUsed = arg_data.isQuery( )

      self.redoIt()
  
  def doItQuery( self ):
    pass
    
  def redoIt( self ):  
    # Clear this out/create it
    self.__dg_modify = OpenMaya.MDGModifier( )
    
    obj = OpenMaya.MObject( )
    
    #create array to house new nodes
    new_nodes = OpenMaya.MObjectArray( )
    
    if len( self.__name_arg ) < 1:
      self.__name_arg = 'bakeLayer'
      
    # Create new node
    if( ( not self.__is_edit_used ) and ( not self.__is_query_used ) ):
    
      new_bake_layer = self.__dg_modify.createNode( bake_layer_node.BakeLayer.PLUGIN_NODE_ID )
      new_nodes.append( new_bake_layer )
      
      self.__this_node_fn.setObject( new_bake_layer )
      
      self.__dg_modify.renameNode( new_bake_layer, self.__name_arg )
      
      self.__dg_modify.doIt( )
      
      self.setResult( self.__this_node_fn.name( ) )
    
    else:
      sel_list_node = OpenMaya.MSelectionList( )
      
      sel_list_node.add( self.__name_arg )
      sel_list_node.getDependNode( 0, obj  )
      
      self.__this_node_fn.setObject( obj )
      
    
    self.__dg_modify.doIt()
    
  def undoIt(self):
    self.__dg_modify.undoIt( )

  def isUndoable(self):
    return True   
    
  @classmethod
  def cmd_creator(cls):
    return OpenMayaMPx.asMPxPtr( cls() )
    
  @classmethod
  def syntax_creator(cls):
    syntax = OpenMaya.MSyntax()
    #syntax.enableQuery() ## not yet, enable this later
    #syntax.enableEdit() ## not yet, enable this later
    syntax.addFlag(cls.NAME_FLAG,
                   cls.NAME_FLAG_LONG,
                   OpenMaya.MSyntax.kString )
  
    
    syntax.useSelectionAsDefault(True)
    syntax.setObjectType(OpenMaya.MSyntax.kSelectionList)
    
    return syntax
    
class ConnectBakeLayersCmd( BakeLayerCmdBase ): 
  """
  A command to quickly connect one low Bake Layer to one high Bake Layer.
  Handling multi-connect will be done in python script
  """   
    
  COMMAND_NAME = 'connectBakeLayer'
  
  #---
  # Flags
  #---
  
  ## Specifies the high bake layer[s] ( CQ )
  HIGH_FLAG = '-h'
  HIGH_FLAG_LONG = '-high'
  
  ## Specifies the low bake layer ( CQ )
  LOW_FLAG = '-l'
  LOW_FLAG_LONG = '-lowLayer'
  
  def __init__( self ):
    OpenMayaMPx.MPxCommand.__init__(self)
    
    self.__isQueryUsed = True
    self.__isEditUsed = False

    self.__low_layer = OpenMaya.MFnDependencyNode( ) # following adam's lead here...see where this goes I suppose
    
    # The Layers for connecting
    self.__low_layers = OpenMaya.MSelectionList( )
    self.__high_layers = OpenMaya.MSelectionList( )
    
    # Used to modify nodes/connections between nodes
    self.__dg_modify = OpenMaya.MDGModifier( )
       
  def doIt(self, args):
    print_info( "doing connect")
    # parse the arguments
    try:
      arg_data = OpenMaya.MArgDatabase( self.syntax( ), args)
    except:
      print_warning( "MArgDatabase Failed" )
      pass
    else:
      
      selection = OpenMaya.MSelectionList( )
      
      high_layer = OpenMaya.MObject( )
      low_layer = OpenMaya.MObject( )
      high_layer_fn = OpenMaya.MFnDependencyNode( )
      low_layer_fn = OpenMaya.MFnDependencyNode( )
    
      selection.add( arg_data.flagArgumentString( self.LOW_FLAG, 0 ) )
      selection.getDependNode( 0, low_layer )
      low_layer_fn.setObject( low_layer )
      print_info( dir( bake_layer_node))
      if not low_layer_fn.typeId( ) == bake_layer_node.BakeLayer.PLUGIN_NODE_ID:
        raise Exception( 'The provided node {0} is not of type{1}.'.format(
                          arg_data.flagArgumentString( self.LOW_FLAG, 0 ),
                          bake_layer_node.BakeLayer.PLUGIN_NODE_NAME ) )
      selection.clear( )
      
      selection.add( arg_data.flagArgumentString( self.HIGH_FLAG, 0 ) )
      selection.getDependNode( 0, high_layer )
      high_layer_fn.setObject( high_layer )
      if not high_layer_fn.typeId( ) == bake_layer_node.BakeLayer.PLUGIN_NODE_ID:
        raise Exception( 'The provided node {0} is not of type{1}.'.format(
                          arg_data.flagArgumentString( self.LOW_FLAG, 0 ),
                          bake_layer_node.BakeLayer.PLUGIN_NODE_NAME ) )
      selection.clear( )
      # Check that both layers are bake layers
      
      
      
      for x in dir( high_layer ):
        print_info( x )
      # Connect the two layers
      
      print_info( 'connecting bake layers')
      self.multi_connect( low_layer,
                          bake_layer_node.BakeLayer.HIGH_CONNECT_NAME,
                          high_layer,
                          bake_layer_node.BakeLayer.LOW_CONNECT_NAME,
                          bake_layer_node.BakeLayer.LOW_CONNECT_LONGNAME )
  
      self.redoIt( )
  
  def redoIt( self ):
    print_info( "redoing connect")
    pass
    
       
  @classmethod
  def cmd_creator(cls):
    return OpenMayaMPx.asMPxPtr( cls() )
  
  @classmethod
  def syntax_creator( cls ):
    syntax = OpenMaya.MSyntax()
    syntax.enableQuery()
    syntax.enableEdit()
    syntax.addFlag( cls.HIGH_FLAG,
                    cls.HIGH_FLAG_LONG,
                    OpenMaya.MSyntax.kString )
    syntax.addFlag( cls.LOW_FLAG,
                    cls.LOW_FLAG_LONG,
                    OpenMaya.MSyntax.kString )
    
    syntax.useSelectionAsDefault( False )
    syntax.setObjectType( OpenMaya.MSyntax.kSelectionList )
    return syntax

class AddToBakeLayerCmd( BakeLayerCmdBase ):
  """
  A command to quickly add an object to a bake layer
  """ 
  
  COMMAND_NAME = 'addToBakeLayer'
  
  #---
  # Flags
  #---
  
  ## Specifies the layer to which objects are being added. ( CQ )
  LAYER_FLAG = '-l'
  LAYER_FLAG_LONG  = '-layer'
  
  ## Specifies the object[s] that are being added to the layer ( CQ )
  OBJECT_FLAG = '-o'
  OBJECT_FLAG_LONG = '-objects'
  
  #---
  # Attrs
  #---
  
  TRANS_CONNECT_ATTR = 'bl'
  TRANS_CONNECT_ATTRLONG = 'bake'
  
  def __init__(self):
    OpenMayaMPx.MPxCommand.__init__(self)
    
    self.__isQueryUsed = False
    self.__isEditUsed = False
    
    self.__layer_node_fn = OpenMaya.MFnDependencyNode( )
    self.__layer_node = OpenMaya.MObject( )
    self.__objects_to_add = OpenMaya.MSelectionList( )
    
  def doIt(self, args ):
    # Parse arguments
    try:
      arg_data = OpenMaya.MArgDatabase( self.syntax( ), args )
    except:
      pass
    
    else:
      selection_list = OpenMaya.MSelectionList( )
      
      # Read all arguments and store them to the appropriate data
      
      # Determine the bake layer to which objects are being added
      
      if arg_data.isFlagSet( self.LAYER_FLAG ):      
           
        selection_list.add( arg_data.flagArgumentString( self.LAYER_FLAG, 0) )
        
        selection_list.getDependNode( 0, self.__layer_node )
        selection_list.clear()
        
        # set object for the layer node fn 
        self.__layer_node_fn.setObject( self.__layer_node )
      
      else:
        raise Exception( 'This command requires that the -layer flag be set' )
      
      
      self.__objects_to_add.clear()
      # Manually specifying object[s] will override selection
      if arg_data.isFlagSet( self.OBJECT_FLAG ):
        self.__objects_to_add.add( arg_data.flagArgumentString( self.OBJECT_FLAG, 0 ) )
      # add objects to command
      
      cmd_objs = OpenMaya.MSelectionList( )
      
      arg_data.getObjects( cmd_objs )
      
      print_info( cmd_objs.length( ) )
      
      iter = OpenMaya.MItSelectionList( cmd_objs, OpenMaya.MFn.kTransform )
      
      while not iter.isDone( ):
        obj = OpenMaya.MObject( )
        iter.getDependNode( obj )
        self.__objects_to_add.add( obj )
        iter.next( )
      
    self.redoIt( )
      
  def redoIt( self ):  
    # Clear this out/create it
    self.__dg_modify = OpenMaya.MDGModifier( )
    
    obj = OpenMaya.MObject()
    
    # Determine transform nodes to attach to the layer
    if self.__objects_to_add.length( ) < 1:
      print_info( "No objects specified in command, using selection" )
      selected = OpenMaya.MSelectionList()
      
      OpenMaya.MGlobal.getActiveSelectionList( selected )
      
      iter = OpenMaya.MItSelectionList( selected, OpenMaya.MFn.kTransform )
      while not iter.isDone( ):
        iter.getDependNode( obj )
        self.__objects_to_add.add( obj )
        iter.next()
        
      if self.__objects_to_add.length( ) < 1:
        raise Exception( 'This command requires that either the -objects flag be set, or one or more objects be selected')
        

    # Connect the bake layer to any selected meshes
    
   
    obj = OpenMaya.MObject()
    iter = OpenMaya.MItSelectionList( self.__objects_to_add, OpenMaya.MFn.kTransform )
    
    while not iter.isDone( ):
      iter.getDependNode( obj )
      
      self.multi_connect( self.__layer_node,
                          bake_layer_node.BakeLayer.LAYER_MEMBERS_NAME,
                          obj,
                          self.TRANS_CONNECT_ATTR,
                          self.TRANS_CONNECT_ATTRLONG )

      iter.next( )
    
    
    
    self.__dg_modify.doIt()

  @classmethod
  def cmd_creator(cls):
    return OpenMayaMPx.asMPxPtr( cls() )
  
  @classmethod
  def syntax_creator(cls):
    syntax = OpenMaya.MSyntax()
    syntax.enableQuery()
    syntax.enableEdit()
    
    syntax.addFlag( cls.LAYER_FLAG,
                    cls.LAYER_FLAG_LONG,
                    OpenMaya.MSyntax.kString )
    
    syntax.addFlag( cls.OBJECT_FLAG,
                    cls.OBJECT_FLAG_LONG,
                    OpenMaya.MSyntax.kString )
    
    syntax.useSelectionAsDefault(True)
    syntax.setObjectType( OpenMaya.MSyntax.kSelectionList )
    return syntax
  
class RemoveFromBakeLayerCmd( BakeLayerCmdBase ):
  """
  A command to quickly remove an object or objects from a bake layer.
  """

  COMMAND_NAME = 'removeFromBakeLayer'
  
  #---
  # Flags
  #---
  
  ## Specifies layer from which objects are being removed ( C )
  LAYER_FLAG = '-l'
  LAYER_FLAG_LONG = '-layer'
  
  ## Specifies the object[s] that are being removed from the layer ( C )
  OBJECT_FLAG = '-o'
  OBJECT_FLAG_LONG = '-objects'
  
  def __init__(self):
    OpenMayaMPx.MPxCommand.__init__(self)
    
    self.isQueryUsed = False
    self.__isEditUsed = False
    
    self.__layer_node = OpenMaya.MObject( )
    self.__layer_node_fn = OpenMaya.MFnDependencyNode( )
    
    self.__objects_to_remove = OpenMaya.MSelectionList( )
  
  def doIt( self, args ):
    
    # Parse arguments
    
    try:
      arg_data = OpenMaya.MArgDatabase( self.syntax( ), args )
    except:
      print_warning( "Arg Database did not work, returned an exception" )
      
    else:
      
      selection_list = OpenMaya.MSelectionList( )
      
      # Determine the bake layer from which you will be removing objects
      
      if arg_data.isFlagSet( self.LAYER_FLAG ):
        
        layer_arg = arg_data.flagArgumentString( self.LAYER_FLAG, 0 )
        try:
          selection_list.add( layer_arg )
        except RuntimeError:
          
          raise Exception( '{0} is not an existing node. Did you type it correctly?'.format( layer_arg ) )
        
        selection_list.getDependNode( 0, self.__layer_node )
        
        # Set object for the layer node Fn.
        self.__layer_node_fn.setObject( self.__layer_node )
        
      else:
        raise Exception ( 'This command requires that the -layer flag be set' )
      
      self.__objects_to_remove.clear( )
      
      # Manually specifying object(s) will override selection
      if arg_data.isFlagSet( self.OBJECT_FLAG ):
        self.__objects_to_remove.add( arg_data.flagArgumentString( self.OBJECT_FLAG, 0 ) )
          
      self.redoIt( )
      
  def redoIt( self ):
      
    self.__dg_modify = OpenMaya.MDGModifier( )
      
    obj = OpenMaya.MObject( )
    path_to_obj = OpenMaya.MDagPath( )
    dep_node_fn = OpenMaya.MFnDependencyNode( )
      
    # Determine the transform nodes to remove from the layer
    if self.__objects_to_remove.length( ) < 1:
      print_info( "No objects specified in command, using selection" )
      selected = OpenMaya.MSelectionList( )
      
      OpenMaya.MGlobal.getActiveSelectionList( selected )
      iter = OpenMaya.MItSelectionList( selected, OpenMaya.MFn.kTransform )
      
      while not iter.isDone( ):
        iter.getDependNode( obj )
        self.__objects_to_remove.add( obj )
        iter.next()
        
      if self.__objects_to_remove.length( ) < 1:
        raise Exception( 'This command requires that either the -objects flag be set, or one or more objects be selected')
        
      iter = OpenMaya.MItSelectionList( self.__objects_to_remove, OpenMaya.MFn.kTransform )

      while not iter.isDone( ):
        plug_array = OpenMaya.MPlugArray( )
        connected_plugs = OpenMaya.MPlugArray( )
        connected_node_fn = OpenMaya.MFnDependencyNode( )
        
        # Get depend node of object to remove
        iter.getDependNode( obj )
        OpenMaya.MDagPath.getAPathTo( obj, path_to_obj )  
        dep_node_fn.setObject( obj )
        
        # Get all connected plugs of that object
        dep_node_fn.getConnections( plug_array )

        for i in ( range (plug_array.length( ) ) ):
          
          plug_array[ i ].connectedTo( connected_plugs, True, False )
          
          for j in( range( connected_plugs.length( ) ) ):

            if connected_plugs[ j ].node( ) == self.__layer_node:
              print_info( 'they match')
            else:
              print_info( 'no match')
              
            connected_node_fn.setObject( connected_plugs[ j ].node( ) )

        iter.next( )
  @classmethod
  def cmd_creator(cls):
    
    return OpenMayaMPx.asMPxPtr( cls( ) )
  
  @classmethod
  def syntax_creator(cls):
    syntax = OpenMaya.MSyntax()
    
    syntax.addFlag( cls.LAYER_FLAG,
                    cls.LAYER_FLAG_LONG,
                    OpenMaya.MSyntax.kString )
    
    syntax.addFlag( cls.OBJECT_FLAG,
                    cls.OBJECT_FLAG_LONG,
                    OpenMaya.MSyntax.kSelectionList )
    
    ##TODO: figure out what to do here
    syntax.useSelectionAsDefault( True )
    syntax.setObjectType( OpenMaya.MSyntax.kSelectionList )
    return syntax 
          
        