

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  set(EXTENSION_NAME WebGLExport)
  set(EXTENSION_HOMEPAGE "https://github.com/xtk/SlicerWebGLExport")
  set(EXTENSION_CATEGORY "Surface Models")
  set(EXTENSION_DESCRIPTION "This module exports the models in a 3D Slicer 4 scene to an interactive webpage using WebGL based on The X Toolkit.")
  set(EXTENSION_CONTRIBUTORS "Daniel Haehn (FNNDSC, CHB), Jean-Christophe Fillion-Robin (Kitware)")
  set(EXTENSION_ICONURL "http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/Base/QTGUI/Resources/Icons/ExtensionDefaultIcon.png?revision=19432&view=co")
  set(EXTENSION_SCREENSHOTURLS "http://xtk.github.com/slicer/abdominalatlas_small.png http://xtk.github.com/slicer/brainatlas_small.png http://xtk.github.com/slicer/blackscene_small.png")
endif()

#-----------------------------------------------------------------------------
set(MODULE_NAME ${EXTENSION_NAME})

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  WebGLExport.py
  )

set(MODULE_PYTHON_RESOURCES
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  )

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  include(${Slicer_EXTENSION_CPACK})
endif()

