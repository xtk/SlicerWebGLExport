from __main__ import vtk, qt, ctk, slicer

import uuid

# this module uses the following from http://www.quesucede.com/page/show/id/python_3_tree_implementation
#
#
# Python 3 Tree Implementation
#
# Copyright (C) 2011, Brett Alistair Kromkamp - brettkromkamp@gmail.com
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of the contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
def sanitize_id( id ): return id.strip().replace( " ", "" )

( _ADD, _DELETE, _INSERT ) = range( 3 )
( _ROOT, _DEPTH, _WIDTH ) = range( 3 )

class Node:
  def __init__( self, name, identifier=None, expanded=True ):
      self.__identifier = ( str( uuid.uuid1() ) if identifier is None else
              sanitize_id( str( identifier ) ) )
      self.name = name
      self.expanded = expanded
      self.__bpointer = None
      self.__fpointer = []

  @property
  def identifier( self ):
      return self.__identifier

  @property
  def bpointer( self ):
      return self.__bpointer

  @bpointer.setter
  def bpointer( self, value ):
      if value is not None:
          self.__bpointer = sanitize_id( value )

  @property
  def fpointer( self ):
      return self.__fpointer

  def update_fpointer( self, identifier, mode=_ADD ):
      if mode is _ADD:
          self.__fpointer.append( sanitize_id( identifier ) )
      elif mode is _DELETE:
          self.__fpointer.remove( sanitize_id( identifier ) )
      elif mode is _INSERT:
          self.__fpointer = [sanitize_id( identifier )]

class Tree:
    def __init__( self ):
        self.nodes = []

    def get_index( self, position ):
        for index, node in enumerate( self.nodes ):
            if node.identifier == position:
                break
        return index

    def create_node( self, name, identifier=None, parent=None ):

        node = Node( name, identifier )
        self.nodes.append( node )
        self.__update_fpointer( parent, node.identifier, _ADD )
        node.bpointer = parent
        return node

    def show( self, position, level=_ROOT ):
        queue = self[position].fpointer
        if level == _ROOT:
            print( "{0} [{1}]".format( self[position].name,
                                     self[position].identifier ) )
        else:
            print( "\t" * level, "{0} [{1}]".format( self[position].name,
                                                 self[position].identifier ) )
        if self[position].expanded:
            level += 1
            for element in queue:
                self.show( element, level )  # recursive call

    def expand_tree( self, position, mode=_DEPTH ):
        # Python generator. Loosly based on an algorithm from 'Essential LISP' by
        # John R. Anderson, Albert T. Corbett, and Brian J. Reiser, page 239-241
        yield position
        queue = self[position].fpointer
        while queue:
            yield queue[0]
            expansion = self[queue[0]].fpointer
            if mode is _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode is _WIDTH:
                queue = queue[1:] + expansion  # width-first

    def is_branch( self, position ):
        return self[position].fpointer

    def __update_fpointer( self, position, identifier, mode ):
        if position is None:
            return
        else:
            self[position].update_fpointer( identifier, mode )

    def __update_bpointer( self, position, identifier ):
        self[position].bpointer = identifier

    def __getitem__( self, key ):
        return self.nodes[self.get_index( key )]

    def __setitem__( self, key, item ):
        self.nodes[self.get_index( key )] = item

    def __len__( self ):
        return len( self.nodes )

    def __contains__( self, identifier ):
        return [node.identifier for node in self.nodes
                if node.identifier is identifier]


#
# WebGLExport
#

class WebGLExport:
  def __init__( self, parent ):
    parent.title = "WebGL Export"
    parent.categories = ["Surface Models"]
    parent.contributor = "Daniel Haehn"
    parent.helpText = """
Grab a beer!
    """
    parent.acknowledgementText = """
    Flex, dude!
    """
    self.parent = parent

#
# qSlicerPythonModuleExampleWidget
#

class WebGLExportWidget:
  def __init__( self, parent=None ):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout( qt.QVBoxLayout() )
      self.parent.setMRMLScene( slicer.mrmlScene )
    else:
      self.parent = parent
    self.logic = WebGLExportLogic()
    if not parent:
      self.setup()
      self.parent.show()

  def setup( self ):

    # Apply button
    self.__exportButton = qt.QPushButton( "Export to WebGL" )
    self.__exportButton.toolTip = "Export to WebGL using XTK."
    self.__exportButton.enabled = True
    self.parent.layout().addWidget( self.__exportButton )

    # Add vertical spacer
    self.parent.layout().addStretch( 1 )

    # connections
    self.__exportButton.connect( 'clicked()', self.onExport )

  def onExport( self ):
    """
    Export to the filesystem.
    """
    self.__exportButton.text = "Working..."
    slicer.app.processEvents()

    output = self.logic.export()

    with open( '/Users/d/Desktop/test.html', 'w' ) as f:
      f.write( output )

    self.__exportButton.text = "Export to WebGL"




class WebGLExportLogic:
  """
  The actual export logic.
  """

  def __init__( self ):
    self.__tree = None
    self.__nodes = {}

    # the html header
    self.__header = """
<html>
<!-- WebGL Export for 3D Slicer4 powered by XTK -- http://goXTK.com -->
  <head>
    <title>WebGL Export</title>
    <script type="text/javascript" src="http://goXTK.com/xtk.js"></script>
    <script type="text/javascript">
      var run = function() {
        var r = new X.renderer('r');
        r.init();


"""

    # the html footer
    self.__footer = """

        r.add(scene);

        r.camera().setPosition%s;

        r.render();
      };
    </script>
  </head>
  <body onload="run()">
    <div id="r" style="background-color: %s; width: 100%%; height: 100%%;"></div>
  </body>
</html>
"""

  def formatFooter( self, threeDIndex ):
    """
    Grab some Slicer environment values like the camera position etc.
    """
    # grab the current 3d view background color
    threeDWidget = slicer.app.layoutManager().threeDWidget( threeDIndex )
    threeDView = threeDWidget.threeDView()
    bgColor = threeDView.backgroundColor.name()

    # grab the current camera position
    cameraNode = slicer.mrmlScene.GetNodeByID( 'vtkMRMLCameraNode' + str( threeDIndex + 1 ) )
    camera = cameraNode.GetCamera()
    cameraPosition = str( camera.GetPosition() )

    # .. and configure the X.renderer
    return self.__footer % ( cameraPosition, bgColor )


  def export( self, threeDIndex=0 ):
    """
    Run through the mrml scene and create an XTK tree based on vtkMRMLModelHierarchyNodes and vtkMRMLModelNodes
    """
    scene = slicer.mrmlScene
    nodes = scene.GetNumberOfNodes()

    self.__nodes = {}

    self.__tree = Tree()
    self.__tree.create_node( "Scene", "scene" )

    for n in xrange( nodes ):

        node = scene.GetNthNode( n )

        self.parseNode( node )

    output = self.__header
    output += self.createXtree( "scene" )
    output += self.formatFooter( threeDIndex )

    return output


  def parseNode( self, node ):
    """
    Parse one mrml node if it is a valid vtkMRMLModelNode or vtkMRMLModelHierarchyNode and add it to our tree
    """

    if not node:
        return

    if ( not node.IsA( 'vtkMRMLModelNode' ) and not node.IsA( 'vtkMRMLModelHierarchyNode' ) ) or ( node.IsA( 'vtkMRMLModelNode' ) and node.GetHideFromEditors() ):
        return

    if self.__nodes.has_key( node.GetID() ):
        return

    parent_node = "scene"

    parentNode = None
    hNode = None

    if node.IsA( 'vtkMRMLModelNode' ):
        parentNode = slicer.app.applicationLogic().GetModelHierarchyLogic().GetModelHierarchyNode( node.GetID() )

        if parentNode:
            parentNode = parentNode.GetParentNode()

    elif node.IsA( 'vtkMRMLModelHierarchyNode' ):
        parentNode = node.GetParentNode()

    if parentNode:
        if parentNode.GetID() == node.GetID():
            return

        parent_node = parentNode.GetID()
        self.parseNode( parentNode )

    if not node.IsA( 'vtkMRMLModelHierarchyNode' ) or not node.GetModelNode():

        self.__nodes[node.GetID()] = node.GetName()
        self.__tree.create_node( node.GetName(), node.GetID(), parent=parent_node )


  def createXtree( self, position, level=_ROOT, parent="" ):
    """
    Convert the internal tree to XTK code.
    """
    queue = self.__tree[position].fpointer
    mrmlId = self.__tree[position].identifier

    output = ' ' * 8 + mrmlId + ' = new X.object();\n'

    if not level == _ROOT:

      n = slicer.mrmlScene.GetNodeByID( mrmlId )
      if n.IsA( 'vtkMRMLModelNode' ):

        # grab some properties
        s = n.GetStorageNode()
        file = s.GetFileName()
        d = n.GetDisplayNode()
        color = str( d.GetColor() )
        opacity = str( d.GetOpacity() )
        visible = str( bool( d.GetVisibility() ) ).lower()

        output += ' ' * 8 + mrmlId + '.load(\'' + file + '\');\n'
        output += ' ' * 8 + mrmlId + '.setColor' + color + ';\n'
        output += ' ' * 8 + mrmlId + '.setOpacity(' + opacity + ');\n'
        output += ' ' * 8 + mrmlId + '.setVisible(' + visible + ');\n'

      output += ' ' * 8 + parent + '.children().push(' + mrmlId + ');\n\n'

    level += 1
    for element in queue:
        output += self.createXtree( element, level, mrmlId )  # recursive call

    return output




class Slicelet( object ):
  """A slicer slicelet is a module widget that comes up in stand alone mode
  implemented as a python class.
  This class provides common wrapper functionality used by all slicer modlets.
  """
  # TODO: put this in a SliceletLib
  # TODO: parse command line arge


  def __init__( self, widgetClass=None ):
    self.parent = qt.QFrame()
    self.parent.setLayout( qt.QVBoxLayout() )

    # TODO: should have way to pop up python interactor
    self.buttons = qt.QFrame()
    self.buttons.setLayout( qt.QHBoxLayout() )
    self.parent.layout().addWidget( self.buttons )
    self.addDataButton = qt.QPushButton( "Add Data" )
    self.buttons.layout().addWidget( self.addDataButton )
    self.addDataButton.connect( "clicked()", slicer.app.ioManager().openAddDataDialog )
    self.loadSceneButton = qt.QPushButton( "Load Scene" )
    self.buttons.layout().addWidget( self.loadSceneButton )
    self.loadSceneButton.connect( "clicked()", slicer.app.ioManager().openLoadSceneDialog )

    if widgetClass:
      self.widget = widgetClass( self.parent )
      self.widget.setup()
    self.parent.show()

class WebGLExportSlicelet( Slicelet ):
  """ Creates the interface when module is run as a stand alone gui app.
  """

  def __init__( self ):
    super( WebGLExportSlicelet, self ).__init__( WebGLExportWidget )


if __name__ == "__main__":
  # TODO: need a way to access and parse command line arguments
  # TODO: ideally command line args should handle --xml

  import sys
  print( sys.argv )

  slicelet = WebGLExportSlicelet()
