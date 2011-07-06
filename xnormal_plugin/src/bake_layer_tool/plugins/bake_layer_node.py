#
#
#

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


