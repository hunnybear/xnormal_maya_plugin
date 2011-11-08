'''
    tgood_xn_exporter
    0.5
    
    copyright (c) 2010 Tyler Good
    This is free software: free as in free speech, and free as in free beer.
    
    This file is quick_edit_window.py
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
import utils

class EditBakeLayerWindow( object ):
  
  def __init__( self, parent, layer ):
    self.parent = parent
    self.layer = utils.get_bake_layer( layer )
    
    self.__window = pmc.window( title = 'Edit Bake Layer' )
    
    self.build( )
    
    self.refresh( )
    
    self.__window.show( )
    
  def build( self ):
    
    form = pmc.formLayout( )
    pmc.setParent( form )
    is_high = utils.is_high( self.layer )
    
    body = pmc.columnLayout( rowSpacing = 4 )
    
    self.name_field = pmc.textFieldGrp( columnWidth = [ 1, 70 ],
                                   label = 'Name',
                                   text = self.layer.name( ),
                                   editable = True )
    
    self.high_low = pmc.radioButtonGrp( columnWidth = [ 1, 70 ],
                                   nrb = 2,
                                   l = 'Layer Type:',
                                   l1 = 'High-poly',
                                   l2 = 'Low-poly' )
    
    self.ray_laybe = pmc.text ( l = 'Max ray Distance:',
                                al = 'center',
                                width = 350 )
    
    float_row = pmc.rowColumnLayout( numberOfRows = 1 )
    
    self.ray_dist_f = pmc.floatFieldGrp( columnWidth = [ 1, 70 ],
                                       nf = 1,
                                       l = 'Front',
                                       pre = 3 )
    
    self.ray_dist_b = pmc.floatFieldGrp( columnWidth = [ 1, 70 ],
                                         nf = 1,
                                         l = 'Back',
                                         pre = 3 )
    
    if is_high:
      self.high_low.setSelect( 1 )
    else:
      self.high_low.setSelect( 2 )
      self.ray_dist_b.setValue1( utils.get_back_ray_dist( self.layer ) )
      self.ray_dist_f.setValue1( utils.get_front_ray_dist( self.layer ) )
    
    button_form = pmc.formLayout( parent = form )

    
    btn_save = pmc.button( label = 'Save',
                           command = self.save_changes )
    
    btn_cancel = pmc.button( label = 'Cancel',
                             command = self.cancel_changes )
    
    
    button_form.attachForm( btn_save, 'top', 0 )
    button_form.attachForm( btn_save, 'left', 0 )
    button_form.attachForm( btn_save, 'bottom', 0 )
    button_form.attachPosition( btn_save, 'right',  2, 50 )
    
    button_form.attachForm( btn_cancel, 'top', 0 )
    button_form.attachPosition( btn_cancel, 'left', 2, 50 )
    button_form.attachForm( btn_cancel, 'bottom', 0 )
    button_form.attachForm( btn_cancel, 'right', 0 )
    
    form.attachForm( body, 'top', 4 )
    form.attachForm( body, 'left', 4 )
    form.attachControl( body, 'bottom', 4, button_form )
    form.attachForm( body, 'right', 4 )
    
    form.attachNone( button_form, 'top' )
    form.attachForm( button_form, 'left', 4 )
    form.attachForm( button_form, 'bottom', 4)
    form.attachForm( button_form, 'right', 4 )
    
    self.refresh( )
    
  def cancel_changes( self, evt ):
    pmc.deleteUI( self.__window )
    
  def save_changes( self, evt ):
    
    self.layer.rename( self.name_field.getText( ) )
    
    if self.high_low.getSelect( ) == 1:
      utils.set_high( self.layer )
    else:
      utils.set_low( self.layer )
      
    ray_dist = [ self.ray_dist_f.getValue1( ), self.ray_dist_b.getValue1( ) ]
    utils.set_bake_ray_dist( self.layer, ray_dist)
    
    self.parent.refresh( )
    
    pmc.deleteUI( self.__window )
  
  def refresh( self ):
    if self.high_low.getSelect( ) == 1:
      self.ray_dist_b.setEnable( False )
      self.ray_dist_f.setEnable( False )
    else:
      self.ray_dist_b.setEnable( True )
      self.ray_dist_f.setEnable( True )