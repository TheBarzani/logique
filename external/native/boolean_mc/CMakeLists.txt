cmake_minimum_required(VERSION 3.19)
project(logique_boolean_mc LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(TWEEDLEDUM_SOURCE_DIR "" CACHE PATH "Explicit clean pinned tweedledum checkout")
execute_process(COMMAND git -C "${TWEEDLEDUM_SOURCE_DIR}" rev-parse HEAD
  OUTPUT_VARIABLE TD_REV OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
if(NOT TD_REV STREQUAL "a3cb238d132825b8e0367d5e96618c5753c1879a")
  message(FATAL_ERROR "Unexpected tweedledum revision: ${TD_REV}")
endif()
execute_process(COMMAND git -C "${TWEEDLEDUM_SOURCE_DIR}" status --porcelain --untracked-files=no
  OUTPUT_VARIABLE TD_DIRTY OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
if(TD_DIRTY)
  message(FATAL_ERROR "Modified dependency sources are unsupported")
endif()
add_executable(boolean_mc main.cpp)
target_include_directories(boolean_mc PRIVATE "${TWEEDLEDUM_SOURCE_DIR}/include")
foreach(dep mockturtle kitty lorina bill percy rang abcresub abcsat)
  target_include_directories(boolean_mc SYSTEM PRIVATE "${TWEEDLEDUM_SOURCE_DIR}/external/${dep}")
endforeach()
target_include_directories(boolean_mc SYSTEM PRIVATE
  "${TWEEDLEDUM_SOURCE_DIR}/external/fmt/include"
  "${TWEEDLEDUM_SOURCE_DIR}/external/nlohmann"
  "${TWEEDLEDUM_SOURCE_DIR}/external/parallel_hashmap")
target_compile_definitions(boolean_mc PRIVATE FMT_HEADER_ONLY DISABLE_NAUTY LIN64 ABC_NAMESPACE=pabc)
file(SHA256 "${TWEEDLEDUM_SOURCE_DIR}/include/tweedledum/Utils/Classical/xag_optimize.h" RECIPE_SHA)
file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/main.cpp" TOOL_SHA)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/build_provenance.json"
  "{\n  \"tweedledum_revision\": \"${TD_REV}\",\n  \"recipe_sha256\": \"${RECIPE_SHA}\",\n  \"tool_source_sha256\": \"${TOOL_SHA}\",\n  \"compiler\": \"${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}\",\n  \"dependency_sources_clean\": true\n}\n")
