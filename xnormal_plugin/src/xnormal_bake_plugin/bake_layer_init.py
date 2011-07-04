'''
Created on Jun 25, 2011

@author: Tyler
'''
import sys

# Maya Imports
import maya.OpenMayaMPx as OpenMayaMPx

# Plugin Imports
import bake_layer_node
import bake_layer_cmds

# For iteration

reload( bake_layer_node )
reload( bake_layer_cmds )

from xnormal_bake_plugin.tool_info import TOOL_NAME
from xnormal_bake_plugin.tool_info import VERSION_NUMBER

VERSION_NUMBER = '0.1'

def initializePlugin( mobject ):
  plugin = OpenMayaMPx.MFnPlugin( mobject, 'Tyler Good', VERSION_NUMBER, 'Any' )
  
  # Register Node
  try:
    plugin.registerNode( bake_layer_node.BakeLayer.PLUGIN_NODE_NAME,
             bake_layer_node.BakeLayer.PLUGIN_NODE_ID,
             bake_layer_node.BakeLayer.node_creator,
             bake_layer_node.BakeLayer.node_initializer,
             OpenMayaMPx.MPxNode.kObjectSet )

  except:
    sys.stderr.write('Failed to register node')
    raise
  
  # Register Commands

  ## Main command
  plugin.registerCommand( bake_layer_cmds.BakeLayerCmd.COMMAND_NAME,
                          bake_layer_cmds.BakeLayerCmd.cmd_creator,
                          bake_layer_cmds.BakeLayerCmd.syntax_creator )
  
  ## Connect Bake layers command
  plugin.registerCommand( bake_layer_cmds.ConnectBakeLayersCmd.COMMAND_NAME,
                          bake_layer_cmds.ConnectBakeLayersCmd.cmd_creator,
                          bake_layer_cmds.ConnectBakeLayersCmd.syntax_creator )
  
  ## Add to bake layer command
  plugin.registerCommand( bake_layer_cmds.AddToBakeLayerCmd.COMMAND_NAME,
                          bake_layer_cmds.AddToBakeLayerCmd.cmd_creator,
                          bake_layer_cmds.AddToBakeLayerCmd.syntax_creator )

  ## Remove from bake layer command
  plugin.registerCommand( bake_layer_cmds.RemoveFromBakeLayerCmd.COMMAND_NAME,
                          bake_layer_cmds.RemoveFromBakeLayerCmd.cmd_creator,
                          bake_layer_cmds.RemoveFromBakeLayerCmd.syntax_creator )

def uninitializePlugin( mobject ):
  plugin = OpenMayaMPx.MFnPlugin( mobject )
  
  plugin.deregisterNode( bake_layer_node.BakeLayer.PLUGIN_NODE_ID )
  plugin.deregisterCommand( bake_layer_cmds.BakeLayerCmd.COMMAND_NAME)
  plugin.deregisterCommand( bake_layer_cmds.ConnectBakeLayersCmd.COMMAND_NAME )
  plugin.deregisterCommand( bake_layer_cmds.AddToBakeLayerCmd.COMMAND_NAME )
  plugin.deregisterCommand( bake_layer_cmds.RemoveFromBakeLayerCmd.COMMAND_NAME )
