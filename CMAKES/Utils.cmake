#Upload Pypi package-----------------------------------------------------------------------
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/Upload.txt
  COMMAND rm -rf dist/*
  COMMAND echo $ENV{Password}
  COMMAND python3 setup.py bdist_wheel
  COMMAND python3 -m twine upload --verbose --password ${Password} --username $ENV{PyPiToken} --repository pypi dist/*
  COMMENT "Upload on Pypi"
  COMMAND make Clean
  )
  
add_custom_target(Upload DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/Upload.txt)



#Cleaning command---------------------------------------------------------------
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/Clean.txt
  COMMAND rm -rf dist CMakeCache.txt cmake_install.cmake *.egg* CMakeCache.txt CMakeFiles 
  COMMENT "Cleaning cmake output files")

add_custom_target(Clean DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/Clean.txt)
