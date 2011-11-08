'''
    tgood_xn_exporter
    0.5
    
    copyright (c) 2010 Tyler Good
    This is free software: free as in free speech, and free as in free beer.
    
    This file is bake_layer_init.py
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
import sys

# Maya Imports
import maya.OpenMayaMPx as OpenMayaMPx

# Plugin Imports
import bake_layer_node
import bake_layer_cmds

from bake_layer_tool import VERSION_NUMBER

def initializePlugin( mobject ):
  plugin = OpenMayaMPx.MFnPlugin( mobject, 'Tyler Good', str( VERSION_NUMBER ), 'Any' )
  
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
