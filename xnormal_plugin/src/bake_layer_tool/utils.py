'''
Created on Jul 2, 2011

@author: Tyler
'''

# TODO: Just combined utils and bake_layer_tools, some things may be redundant, fix this.

import os
import os.path
import _winreg
import subprocess

import xml.dom.minidom
import xml.parsers.expat

import pymel.core as pmc

HIGH_CONNECT_ATTR = 'hc'
LOW_CONNECT_ATTR = 'lc'
LAYER_MEMBERS_ATTR = 'lm'

#==============================================================================
# Layer Members
#==============================================================================

def select_from_bake_layer( layer ):
  
  node = get_bake_layer( layer )
  
  if node == None:
    pmc.error( 'select_from_bake_layer requires one "BakeLayer" node.')
    

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
    pmc.error( 'add_to_bake_layer requires one "BakeLayer" node.')
  
  # get the list of nodes for the objects
  
  if objects == None:
    pmc.warning( 'No objects specified, using selection' )
    obj_list = pmc.ls( sl = True, typ = 'transform' ) 
  
  elif isinstance( objects, pmc.nt.Transform ):
    obj_list = [ objects ]
  
  elif isinstance( pmc.PyNode( objects ), pmc.nt.Transform ):
    obj_list = [ pmc.PyNode( objects ) ]
    
  elif isinstance( object, [ tuple, list ] ):
    obj_list = objects
    
  else:
    pmc.error( 'Objects supplied for add_to_bake_layer command were invalid' )

  if len( obj_list ) < 1:
    pmc.error( 'No valid objects were supplied or selected for the bake_layer_command' )
  
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
    pmc.error( 'connect_layers requires one low-poly Bake Layer be specified.' )
    return False

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
    pmc.error( 'connect_layers requires at least one high-poly Bake Layer be specified.' )
    return False
  
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
        
def set_bake_ray_dist( layer, dist ):
  node = get_bake_layer( layer )
  node.setAttr( 'mrd', dist )

      
#==============================================================================
# Query Layer
#==============================================================================

def get_front_ray_dist( layer ):
  node = get_bake_layer( layer )
  
  return node.getAttr( 'mrd' )[ 0 ]

def get_back_ray_dist( layer ):
  node = get_bake_layer( layer )
  
  return node.getAttr( 'mrd' )[ 1 ]

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
    pmc.error( 'get_connected_low_layers requires one Bake Layer node.' )
    return False
  
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
    pmc.error( 'get_connected_high_layers requires one Bake Layer node.' )
    return False  
    
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
  
  if bake_mesh == False:
    return False
  
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
  
  if len( meshes ) == 0:
    return False
  
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
  if low_export == False:
    return False
  low_mesh = LowMesh( low_export,
                      max_ray_distance_back=str( get_back_ray_dist( low_node ) ),
                      max_ray_distance_front=str( get_front_ray_dist( low_node ) ) )
  
  base_file = get_base_export_file( low_node )
  
  high_exports = [ ]
  
  # xNormal related vars
  xn_loc = get_xn_location( )
  if xn_loc == None:
    pmc.error( 'No location for xNormal has been set' )
    return False
  
  for high in get_connected_high_layers( low_node ):
    ex_obj = export_layer( high )
    if not ex_obj == False:
      to_export = HighMesh( ex_obj )
      if not to_export == False:
        high_exports.append( to_export  )
        
        
    
    
  # The XML DOM object
  config = XNConfigSettings( )
  
  # xml settings file for xNormal
  xml_path = config.file_path
  
  # set up the XML file for baking
  print low_mesh
  print high_exports
  config.set_bake_meshes( [ low_mesh ], high_exports ) 
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

##-------------------------------------
## generic config file utilities
##-------------------------------------


def get_cfg_settings( cfg_file_path = None, settings = [ ] ):
    xml_cfg = XMLSettings( cfg_file_path )
    return xml_cfg.get_settings( settings )

def set_cfg_settings( cfg_file_path, settings = { }, append = False, remove = False ):
    if remove == False:
        cfg_xml = XMLSettings( cfg_file_path  )

        cfg_xml.write_settings( settings, append = append )

    else:
        if os.path.exists( cfg_file_path ):
            os.remove( cfg_file_path )

class XMLSettings( object ):
    PREFS_DIR = None

    def __init__( self, cfg_file_path = None ):
      if cfg_file_path == None:
        self.cfg_file_path = self.PREFS_DIR
      else: 
        self.cfg_file_path = cfg_file_path

      self.return_settings = { }

      try:
        self.cfgs = xml.dom.minidom.parse( self.cfg_file_path )

      except ( xml.parsers.expat.ExpatError, IOError ):
        impl = xml.dom.minidom.getDOMImplementation( )
        self.cfgs = impl.createDocument( None, 'settings', None )

      self.top_element = self.cfgs.documentElement        

    def get_settings( self, settings ):
        
      if isinstance( settings, ( list, tuple ) ):

        for setting in settings:
          elements = self.cfgs.getElementsByTagName( setting )
          data = ''
          for element in elements:
            data = { setting : self.get_setting( element ) }
              
        
              
      elif isinstance( settings, ( str, unicode ) ):

        elements = self.cfgs.getElementsByTagName( settings )
        data = ''
        for element in elements: 
          data = self.get_setting( element )
            
      return data
        

    def get_setting( self, element ):
      ''' 
      Get a single setting from this XML_Settings object.  I won't be calling this
      directly, but I will use it for getting individual elements for get_settings.
      '''
      # List Elements
      if element.getAttribute( 'type' ) == 'list':
        return_list = [ ]
        for node in element.getElementsByTagName( 'item' ):
          return_list.append( self.get_setting( node ) )

        return return_list
      
      # Dict Elements
      elif element.getAttribute( 'type' ) == 'dict':
        return_dict = { }
        for node in element.childNodes:
          if node.nodeType == node.ELEMENT_NODE:

            return_dict[ node.tagName ] = self.get_setting( node )

        return return_dict
      
      elif element.getAttribute( 'type' ) == 'bool':
        # First see if the element has any data
        if element.childNodes:
          if element.firstChild.nodeType == element.firstChild.TEXT_NODE:
            data = element.firstChild.data 
          else:
            # This is most likely an error
            data = None
        else:
          # If the node is empty
          data = None
        if data == 'True':
          return True
        elif data == 'False':
          return False
        else:
          return None
        

      # String Elements
      else:
        # First see if the element has any data
        if element.childNodes:
          if element.firstChild.nodeType == element.firstChild.TEXT_NODE:
            data = element.firstChild.data 
          else:
            # This is most likely an error
            data = None
        else:
          # If the node is empty
          data = ''
        return data

    def write_settings( self, settings = { }, append = False ):

      for setting in settings.keys( ):

        val = settings[ setting ]

        self.add_settings_element( setting, val, self.top_element, append )

      # Unfortunately, the human readable toxml function (toprettyxml) is broken and creates
      # xml with incorrect whitespace.  due to this, the script is currently creating ugly
      # non-human readable( at least without much effort) xml.  apologies, all around
      
      cfg_file = open( self.cfg_file_path, 'w')
      cfg_file.write( self.cfgs.toxml( ) )
      cfg_file.close( )

    def add_settings_element( self, setting, value, parent, append= False ):

        # Get/create the element node

        # Do this for dicts and strings
        if parent.getAttribute( 'type' ) != 'list':

            # If there is another tag here that is using the same name, use it, otherwise make one
            if parent.getElementsByTagName( setting ):
                setting_node = parent.getElementsByTagName( setting )[ 0 ]
            else:
                setting_node = self.cfgs.createElement( setting )
        # Because the elements of a list will have the same tag name, bypass the overwrite
        # bits used for strings/dicts
        else:
            setting_node = self.cfgs.createElement( setting )
        

        if isinstance( value, list ):
            if setting_node.getAttribute( 'type' ) == 'list' and append == True:
                item_elements = [ ]
                items_to_add = [ ]
                children =  setting_node.childNodes
                for node in children:
                    if node.tagName == 'item':
                        item_elements.append( node )
                    
                items = [ ]
                for item in item_elements:
                    items.append( self.get_setting( item ) )

                for val in value:
                    if val not in items:
                        items_to_add.append( val )
            else:
                while setting_node.childNodes:
                    for child in setting_node.childNodes:
                        setting_node.removeChild( child )
                        
                items_to_add = value
                    
            
            setting_node.setAttribute( 'type', 'list' )
            for item in items_to_add:
                self.add_settings_element( 'item', item, setting_node )
            parent.appendChild( setting_node )

        elif isinstance( value, dict ):
            setting_node.setAttribute( 'type', 'dict' )
            for key in value.keys( ):
                self.add_settings_element( key, value[ key ], setting_node )
            parent.appendChild( setting_node )

        elif isinstance( value, bool ):
          setting_node.setAttribute( 'type', 'bool' )
          for child in setting_node.childNodes:
            setting_node.removeChild( child )
          setting_text = self.cfgs.createTextNode( str( value ) )
          setting_node.appendChild( setting_text )
          parent.appendChild( setting_node )
        
        else:
            setting_node.setAttribute( 'type', 'string' )
            for child in setting_node.childNodes:
                setting_node.removeChild( child )
            setting_text = self.cfgs.createTextNode( str( value ) )
            setting_node.appendChild( setting_text )
            parent.appendChild( setting_node )


##-------------------------------------
## Registry Utilities
##-------------------------------------
'''
thanks to Daniel Kinnaer
http://code.activestate.com/recipes/66011-reading-from-and-writing-to-the-windows-registry/
'''
    
def get_env_var( key ):
    registry = _winreg.ConnectRegistry( None, _winreg.HKEY_CURRENT_USER )
    env_key = _winreg.OpenKey( registry, r'Environment' )

    var_value = _winreg.QueryValueEx( env_key, key )[ 0 ]

    _winreg.CloseKey( env_key )
    _winreg.CloseKey( registry )

    return var_value        

def set_env_var( key, value ):

    registry = _winreg.ConnectRegistry( None, _winreg.HKEY_CURRENT_USER )
    env_key = _winreg.OpenKey( registry, r'Environment', 0, _winreg.KEY_WRITE )

    try:
        _winreg.SetValueEx( env_key, key, 0, _winreg.REG_SZ, value )
    except EnvironmentError:
        print "Encountered problems writing to the registry" 

    _winreg.CloseKey( env_key )
    _winreg.CloseKey( registry )

def get_app_data( ):
    registry = _winreg.ConnectRegistry( None, _winreg.HKEY_CURRENT_USER )
    env_key = _winreg.OpenKey( registry, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders' )

    var_value = _winreg.QueryValueEx( env_key, 'AppData' )[ 0 ]

    _winreg.CloseKey( env_key )
    _winreg.CloseKey( registry )

    if '%USERPROFILE%' in var_value:
        var_value = var_value.replace( '%USERPROFILE%', os.environ[ 'USERPROFILE' ] )

    return var_value

def get_doc_folder( ):
    registry = _winreg.ConnectRegistry( None, _winreg.HKEY_CURRENT_USER )
    env_key = _winreg.OpenKey( registry, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders' )

    var_value = _winreg.QueryValueEx( env_key, 'Personal' )[ 0 ]

    _winreg.CloseKey( env_key )
    _winreg.CloseKey( registry )

    if '%USERPROFILE%' in var_value:
        var_value = var_value.replace( '%USERPROFILE%', os.environ[ 'USERPROFILE' ] )

    return var_value

##-------------------------------------
## Maya Utilities
##-------------------------------------

# Basically just convenience functions

def set_bake_normals( setting ):
  prefs = BakeLayersPrefs( )
  prefs.set_bake_normals( setting )
  
def set_bake_ao( setting ):
  prefs = BakeLayersPrefs( )
  prefs.set_bake_ao( setting )

def get_bake_normals( ):
  prefs = BakeLayersPrefs( )
  return bool( prefs.get_bake_normals( ) )
  
def get_bake_ao( ):
  prefs = BakeLayersPrefs( )
  return bool( prefs.get_bake_ao( ) )

def get_xn_location( ):
  prefs = BakeLayersPrefs( )
  return prefs.get_xn_location( )

def set_xn_location( location ):
  prefs = BakeLayersPrefs( )
  prefs.set_xn_location( location )

# Creates a prefs xml file for the bake_layer_tool stuff

class BakeLayersPrefs( XMLSettings ):
  PREFS_DIR = pmc.internalVar( userPrefDir = True ) + r'xn_bake_prefs.cfg'
  def set_xn_location( self, location ):
    self.write_settings( {'xn_location' : location }, False )
    
  def get_xn_location( self ):
    return self.get_settings( 'xn_location' )
  
  def set_bake_normals( self, setting ):
    self.write_settings( { 'gen_normal' : setting } )
  
  def get_bake_normals( self ):
    return self.get_settings( 'gen_normal' )
  
  def set_bake_ao( self, setting ):
    self.write_settings( { 'gen_ao' : setting } )
    
  def get_bake_ao( self ):
    return self.get_settings( 'gen_ao' )

##-------------------------------------
## XNormal xml config file utilities
##-------------------------------------

class XNConfigSettings( object ):
    '''
    holds all of the data for an xnormal configuration file.  This is redundant
    with a lot of the stuff in the XMLSettings class, so I should fold these
    together where possible soon
    '''
    
    def __init__( self, cfg_file_path = None ):
      
      
      
      self.file_path = cfg_file_path

      if self.file_path != None:
        try:
          self.config = xml.dom.minidom.parse( cfg_file_path )
        except (xml.parsers.expat.ExpatError, IOError ):
          try:
            self.config = xml.dom.minidom.parse( get_doc_folder( ) + '\\xNormal\\last.xml' )
          except (xml.parsers.expat.ExpatError, IOError ):
            impl = xml.dom.minidom.getDOMImplementation( )
            self.config = impl.createDocument( None, 'settings', None )
          self.file_path = get_doc_folder( ) + '\\xNormal\\last.xml'

      else:
        try:
          self.config = xml.dom.minidom.parse( get_doc_folder( ) + '\\xNormal\\last.xml' )
        except (xml.parsers.expat.ExpatError, IOError ):
          impl = xml.dom.minidom.getDOMImplementation( )
          self.config = impl.createDocument( None, 'settings', None )
        self.file_path = get_doc_folder( ) + '\\xNormal\\last.xml'

      self.top_element = self.config.documentElement
      
      try:
        self.high_node = self.config.getElementsByTagName( 'HighPolyModel' )[ 0 ]
      except IndexError:
        self.high_node = self.config.createElement( 'HighPolyModel' )
        self.top_element.appendChild( self.high_node )
        
      try:
        self.low_node = self.config.getElementsByTagName( 'LowPolyModel' )[ 0 ]
      except IndexError:
        self.low_node = self.config.createElement( 'LowPolyModel' )
        self.top_element.appendChild( self.low_node )
      
      self.high_meshes = self.get_high_meshes( )
      self.low_meshes = self.get_low_meshes( )


    def get_high_meshes( self ):
      """
      Returns obj file paths for high meshes in the xml file
      """
      high_list = self.config.getElementsByTagName( 'HighPolyModel' )[ 0 ]
      high_meshes = high_list.getElementsByTagName( 'Mesh' )
      return high_meshes

    def get_low_meshes( self ):
      low_list = self.config.getElementsByTagName( 'LowPolyModel' )[ 0 ]
      low_meshes = low_list.getElementsByTagName( 'Mesh' )
      return low_meshes

    def add_mesh( self, mesh_type, obj ):

      # Low Poly
      if mesh_type == 'low':
        low_meshes = self.get_low_meshes( )
        
      elif mesh_type == 'high':
        high_meshes = self.get_high_meshes( )

    def set_bake_meshes( self, low_meshes, high_meshes ):
        
      # Create list of to bake obj files for iteration
      low_objs = [ ]
      high_objs = [ ]


      # Set all meshes to not visible
      for mesh in self.high_meshes:
        mesh.setAttribute( 'Visible', 'false' )
        high_objs.append( mesh.getAttribute( 'File' ) )

      for mesh in self.low_meshes:
        mesh.setAttribute( 'Visible', 'false' )
        low_objs.append( mesh.getAttribute( 'File' ) )

      # Set settings on meshes to use for bake
      print low_meshes
      for mesh in low_meshes:
        if mesh in low_objs:
          for xml_mesh in self.low_meshes:
            if xml_mesh.getAttribute( 'File' ) == mesh.get_obj( ):
              xml_mesh.setAttribute( 'Visible', 'true' )
              for k, v in mesh.settings.items( ):
                xml_mesh.setAttribute( k, v )

        else:
          new_node = self.config.createElement( "Mesh" )
          for k, v in mesh.settings.items( ):
              new_node.setAttribute( k, v )
          self.low_node.appendChild( new_node )
          self.low_meshes.append( mesh )
              

      for mesh in high_meshes:
        if mesh in high_objs:
          
          for xml_mesh in self.high_meshes:
            if xml_mesh.getAttribute( 'File' ) == mesh:
              xml_mesh.setAttribute( 'Visible', 'true' )
              for k, v in mesh.settings.items( ):
                xml_mesh.setAttribute( k , v )
        else:
          new_node = self.config.createElement( "Mesh" )
          for k, v in mesh.settings.items( ):
              new_node.setAttribute( k, v )
          self.high_node.appendChild( new_node )
          self.high_meshes.append( mesh )

        self.write_config( )

    def set_base_file( self,
                       base_file ):
      
      try:
        generate_maps = self.config.getElementsByTagName( 'GenerateMaps' )[ 0 ]
      except IndexError:
        generate_maps = self.config.createElement( 'GenerateMaps' )
        self.top_element.appendChild( generate_maps )
      
      generate_maps.setAttribute( 'File', base_file )
      
      self.write_config( )
    
    def bake_normals(self, switch):
      self.set_bake_setting( 'GenNormals', str( switch ).lower( ) )
    def bake_ao( self, switch ):
      self.set_bake_setting( 'GenAO', str( switch ).lower( ) )
    
    def set_bake_setting( self, setting, value ):
      generate_maps = self.config.getElementsByTagName( 'GenerateMaps' )[ 0 ]

      generate_maps.setAttribute( setting, value )
      
      self.write_config( )

    def write_config( self ):
        f = open( self.file_path, 'w' )
        self.config.writexml( f )
            

        
class HighMesh( object ):
  """
  Inputs:
    * obj:              STRING   file name for .obj file
    * avg_normals:      STRING   configuration value for Xn
    * base_tex_is_tsnm: STRING   configuration value for Xn
  """
  def __init__( self,
                obj,
                avg_normals = 'UseExportedNormals',
                base_tex_is_tsnm = 'false',
                ignore_per_vertex_color = "true",
                scale = "1.000000" ):
    self.obj = obj
    self.settings = {
        'AverageNormals' : avg_normals,
        'BaseTexIsTSNM' : base_tex_is_tsnm,
        'File' : obj,
        'IgnorePerVertexColor' : ignore_per_vertex_color,
        'Scale' : scale
        }
 
class LowMesh( object ):

    def __init__( self,
                  obj,
                  alpha_test_value ="127",
                  average_normals ="UseExportedNormals",
                  backface_cull ="true",
                  batch_protect = "false",
                  cast_shadows="true",
                  fresnel_refractive_index = "1.330000",
                  highpoly_normals_override = "true",
                  match_uvs="false", matte="false",
                  max_ray_distance_back="0.500000",
                  max_ray_distance_front = "0.500000",
                  nm_swizzle_x="X+", nm_swizzle_y="Y+", nm_swizzle_z="Z+", nm_tangent_space="true",
                  recieve_shadows="true",
                  reflect_hdr_mult ="1.000000",
                  scale="1.000000", transparency_mode ="None",
                  use_cage ="false",
                  use_fresnel ="false",
                  use_per_vertex_colors ="true",
                  vdm_swizzle_x="X+",vdm_swizzle_y="Y+",
                  vdm_swizzle_z="Z+",
                  vector_displacement_ts="false",
                  visible= "true" ):
        
        self.obj = obj
        self.settings = {
            'AlphaTestValue' : alpha_test_value,
            'AverageNormals' : average_normals,
            'BackfaceCull' : backface_cull,
            'BatchProtect' : batch_protect,
            'CastShadows' : cast_shadows,
            'File' : obj,
            'FresnelRefractiveIndex' : fresnel_refractive_index,
            'HighpolyNormalsOverrideTangentSpace' : highpoly_normals_override,
            'MatchUVs' : match_uvs,
            'Matte' : matte,
            'MaxRayDistanceBack' : max_ray_distance_back,
            'MaxRayDistanceFront' : max_ray_distance_front,
            'NMSwizzleX' : nm_swizzle_x,
            'NMSwizzleY' : nm_swizzle_y,
            'NMSwizzleZ' : nm_swizzle_z,
            'NMTangentSpace' : nm_tangent_space,
            'ReceiveShadows' : recieve_shadows,
            'ReflectHDRMult' : reflect_hdr_mult,
            'Scale' : scale,
            'TransparencyMode' : transparency_mode,
            'UseCage' : use_cage,
            'UseFresnel' : use_fresnel,
            'UsePerVertexColors' : use_per_vertex_colors,
            'VDMSwizzleX' : vdm_swizzle_x,
            'VDMSwizzleY' : vdm_swizzle_y,
            'VDMSwizzleZ' : vdm_swizzle_z,
            'VectorDisplacementTS' : vector_displacement_ts,
            'Visible' : visible
    
            }
    

    


##-------------------------------------
## User Roaming Profile config file utilities
##-------------------------------------

def set_roaming_profile_options( settings = { } ):

    # The directory for the app data
    user_app_data = get_app_data( )
    app_data_dir= user_app_data + '\\goodUtils'
    app_data_cfg_file = app_data_dir + '\\.tgood_xn_exporter.cfg' 

    if not os.path.exists( app_data_dir ):
        os.mkdir( app_data_dir )

    set_cfg_settings( app_data_cfg_file, settings )

def get_roaming_profile_options( settings = [ ] ):
    user_app_data = get_app_data( )
    app_data_dir= user_app_data + '\\goodUtils'
    app_data_cfg_file = app_data_dir + '\\.tgood_xn_exporter.cfg'

    if not os.path.exists( app_data_cfg_file ):
        return None
    else:
        return get_cfg_settings( app_data_cfg_file, settings )
