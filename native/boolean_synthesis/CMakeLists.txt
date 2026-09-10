cmake_minimum_required(VERSION 3.18)
project(vcgc_boolean_synthesis LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include(FetchContent)
if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()
FetchContent_Declare(caterpillar
  URL https://github.com/gmeuli/caterpillar/archive/4c6f766cd0ffc62d37ab45edfe80c9f1eae44764.tar.gz
  SOURCE_SUBDIR vcgc_no_upstream_build)
FetchContent_MakeAvailable(caterpillar)
# The reference uncompute handler frees a wire but leaves its stale stack entry.
# Nested best-fit recomputation must expose the previous mapping after cleanup.
file(COPY ${caterpillar_SOURCE_DIR}/include/caterpillar
  DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/compat)
file(READ ${caterpillar_SOURCE_DIR}/include/caterpillar/synthesis/lhrs.hpp lhrs_source)
string(REGEX MATCHALL "release_ancilla\\( t \\)" matches "${lhrs_source}")
list(LENGTH matches match_count)
if(NOT match_count EQUAL 1)
  message(FATAL_ERROR "Pinned LHRS source changed; review the uncompute stack fix")
endif()
string(REPLACE "release_ancilla( t );"
  "release_ancilla( t );\n                node_to_qubit[node].pop(); // VCGC: restore previous mapping"
  lhrs_patched "${lhrs_source}")
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/compat/caterpillar/synthesis/lhrs.hpp "${lhrs_patched}")
file(READ ${caterpillar_SOURCE_DIR}/include/caterpillar/synthesis/strategies/best_fit_mapping_strategy.hpp best_fit_source)
set(cell_marker "  uint32_t size() const\n")
string(FIND "${best_fit_source}" "${cell_marker}" cell_marker_position)
if(cell_marker_position EQUAL -1)
  message(FATAL_ERROR "Pinned best-fit source changed; review the cell fanout fix")
endif()
# Eager cleanup must count edges between mapped cells, not original logic gates.
string(REPLACE "${cell_marker}"
  "  uint32_t fanout_size( node<Ntk> const& n ) const\n  {\n    return (*_cell_fanout)[n];\n  }\n\n${cell_marker}"
  best_fit_patched "${best_fit_source}")
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/compat/caterpillar/synthesis/strategies/best_fit_mapping_strategy.hpp "${best_fit_patched}")
add_executable(boolean_synthesis main.cpp)
target_include_directories(boolean_synthesis BEFORE PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/compat)
target_include_directories(boolean_synthesis PRIVATE ${caterpillar_SOURCE_DIR}/include)
foreach(dep mockturtle tweedledum kitty lorina fmt ez sparsepp percy easy bill json rang abcsat)
  target_include_directories(boolean_synthesis SYSTEM PRIVATE ${caterpillar_SOURCE_DIR}/lib/${dep})
endforeach()
target_compile_definitions(boolean_synthesis PRIVATE FMT_HEADER_ONLY DISABLE_NAUTY LIN64 ABC_NAMESPACE=pabc)
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
  target_compile_options(boolean_synthesis PRIVATE -Wno-deprecated-declarations)
endif()
