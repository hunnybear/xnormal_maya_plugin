'''
    tgood_xn_exporter
    0.5
    
    copyright (c) 2010 Tyler Good
    This is free software: free as in free speech, and free as in free beer.
    
    This file is bake_layer_node.py
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

# Maya API related imports
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya


# Because I'm lazy

print_info = OpenMaya.MGlobal.displayInfo
print_warning = OpenMaya.MGlobal.displayWarning
print_error = OpenMaya.MGlobal.displayError

    
# -----------------------------------------------------------------------------
# Node Definition
# -----------------------------------------------------------------------------


class BakeLayer( OpenMayaMPx.MPxObjectSet ):
  PLUGIN_NODE_NAME = 'BakeLayer'
  PLUGIN_NODE_ID = OpenMaya.MTypeId( 0x00333 )

  # ---
  # Attributes
  #---

  #a_layer_name = OpenMaya.MObject( )
  a_bool_is_high = OpenMaya.MObject( )
  IS_HIGH_NAME = 'hp'
  IS_HIGH_LONGNAME = 'HighPolyLayer'
  
  a_layer_members = OpenMaya.MObject( )
  LAYER_MEMBERS_NAME = 'lm'
  LAYER_MEMBERS_LONGNAME = 'layerMembers'
  
  a_high_connect = OpenMaya.MObject( )
  HIGH_CONNECT_NAME = 'hc'
  HIGH_CONNECT_LONGNAME = 'highConnect'
  
  a_low_connect = OpenMaya.MObject( )
  LOW_CONNECT_NAME = 'lc'
  LOW_CONNECT_LONGNAME = 'lowConnect'
  
  a_max_ray_distance = OpenMaya.MObject( )
  MAX_RAY_NAME = 'mrd'
  MAX_RAY_LONGNAME = 'maxRayDistance'
  
  def set_low_layer( self ):
    # Disconnect all low layers
    
    # Set low connect to hidden
    
    pass
    
  def set_high_layer( self ):
    pass

  @classmethod
  def node_creator( cls ):
    return OpenMayaMPx.asMPxPtr( cls( ) )
  
  @classmethod
  def node_initializer(cls):
    
    compound_attr = OpenMaya.MFnCompoundAttribute( )
    num_attr = OpenMaya.MFnNumericAttribute( )
    typed_attr = OpenMaya.MFnTypedAttribute( )
    
    # Input Attributes
    ## Is the layer High poly
    
    
    cls.a_bool_is_high = num_attr.create( 
                                            cls.IS_HIGH_LONGNAME,
                                            cls.IS_HIGH_NAME,
                                            OpenMaya.MFnNumericData.kBoolean,
                                            0 )
    num_attr.setWritable( True )
    num_attr.setStorable( True )
    num_attr.setReadable( True )
    num_attr.setKeyable( False )
    
    # Not doing this compound for now
    # TODO: figure out what's crashign with compound attrs
    
    #cls.a_low_connect = compound_attr.create(
    #                                      cls.LOW_CONNECT_LONGNAME,
    #                                      cls.LOW_CONNECT_NAME )
    #compound_attr.setWritable( True )
    #compound_attr.setStorable( True )
    #compound_attr.setReadable( True )
    #compound_attr.setKeyable( False )
    
    cls.a_low_connect = num_attr.create(cls.LOW_CONNECT_LONGNAME,
                                        cls.LOW_CONNECT_NAME,
                                        OpenMaya.MFnNumericData.kBoolean,
                                        1 )
    
    
    # Output Attributes
    ## Layer Members
    cls.a_layer_members = num_attr.create(cls.LAYER_MEMBERS_LONGNAME,
                                          cls.LAYER_MEMBERS_NAME,
                                          OpenMaya.MFnNumericData.kBoolean,
                                          1 )
    
    num_attr.setWritable( True )
    num_attr.setStorable( True )
    num_attr.setReadable( True )
    num_attr.setKeyable( False )
    
    cls.a_high_connect = num_attr.create(cls.HIGH_CONNECT_LONGNAME,
                                         cls.HIGH_CONNECT_NAME,
                                         OpenMaya.MFnNumericData.kBoolean,
                                         1)
    
    num_attr.setWritable( True )
    num_attr.setStorable( True )
    num_attr.setReadable( True )
    num_attr.setKeyable( False )
    
    cls.a_max_ray_distance = num_attr.create( cls.MAX_RAY_LONGNAME,
                                              cls.MAX_RAY_NAME,
                                              OpenMaya.MFnNumericData.k2Float,
                                              1 )
                                              
    num_attr.setWritable( True )
    num_attr.setStorable( True )
    num_attr.setReadable( True )
    num_attr.setKeyable( False )
    
    # Add the attributes 
    cls.addAttribute( cls.a_bool_is_high )
    cls.addAttribute( cls.a_high_connect )
    cls.addAttribute( cls.a_layer_members )
    cls.addAttribute( cls.a_low_connect )
    cls.addAttribute( cls.a_max_ray_distance )


