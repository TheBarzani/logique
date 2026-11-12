cmake_minimum_required(VERSION 3.18)
project(logique_fast_depth_api_probe LANGUAGES CXX)
# A separate private project: no production strategy dispatch is enabled here.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT DEFINED FETCHCONTENT_SOURCE_DIR_CATERPILLAR)
  message(FATAL_ERROR "Specify the existing pinned Caterpillar source explicitly")
endif()
add_subdirectory(../.. bridge EXCLUDE_FROM_ALL)
add_executable(native_fast_depth_probe probe.cpp)
target_include_directories(native_fast_depth_probe BEFORE PRIVATE
  ${CMAKE_CURRENT_BINARY_DIR}/bridge/compat)
target_include_directories(native_fast_depth_probe PRIVATE
  ${FETCHCONTENT_SOURCE_DIR_CATERPILLAR}/include)
foreach(dep mockturtle tweedledum kitty lorina fmt ez sparsepp percy easy bill json rang abcsat)
  target_include_directories(native_fast_depth_probe SYSTEM PRIVATE
    ${FETCHCONTENT_SOURCE_DIR_CATERPILLAR}/lib/${dep})
endforeach()
target_compile_definitions(native_fast_depth_probe PRIVATE
  FMT_HEADER_ONLY DISABLE_NAUTY LIN64 ABC_NAMESPACE=pabc)
target_compile_options(native_fast_depth_probe PRIVATE -Wno-deprecated-declarations)
