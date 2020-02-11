set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set any operating-system dependent flags for the compiler
if (WIN32)
    set(COMPILE_FLAGS "/arch:AVX")
else()
    set(COMPILE_FLAGS "-mavx")
endif()

# Include our own source files
set(SOURCE_FILES
    "common.cpp"
    "common.hpp"
    "AnimationProxy.cpp"
    "AnimationProxy.hpp"
    "ErrorTable.cpp"
    "ErrorTable.hpp"
    "SelectionProxy.cpp"
    "SelectionProxy.hpp"
    "Selector.cpp"
    "Selector.hpp"
    "SelectionManager.cpp"
    "SelectionManager.hpp"
    "Interpolator.cpp"
    "Interpolator.hpp"
    "MayaUtils.cpp"
    "MayaUtils.hpp"
    "ReduceCommand.cpp"
    "ReduceCommand.hpp"
	"SelectCommand.cpp"
    "SelectCommand.hpp"
    "pluginMain.cpp"
)
add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

# Include Maya, OpenCL, and Eigen source files
target_include_directories(${PROJECT_NAME} PRIVATE Maya::Maya)
include_directories(${OpenCL_INCLUDE_DIRS})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/eigen-git-mirror/Eigen)

# Link Maya and OpenCL (Eigen is header only)
set(LIBS ${OpenCL_LIBRARY} Maya::Maya)
target_link_libraries (${PROJECT_NAME} PRIVATE ${LIBS})

# Set our own compiler options
target_compile_options(${PROJECT_NAME} PRIVATE ${COMPILE_FLAGS})

# Format as a Maya plugin.
MAYA_PLUGIN(${PROJECT_NAME})

# Setup the maya module
install(DIRECTORY "../maya/" DESTINATION ./SalientPoses)
install(TARGETS ${PROJECT_NAME} ${MAYA_TARGET_TYPE} DESTINATION ./SalientPoses/plug-ins)
