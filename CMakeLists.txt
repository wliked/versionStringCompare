###############################################################
#
# Copyright (c) 2016 : wang liang
# License : Distributed under the GNU General Public License
# created on : 4/02/2016,  by wang liang (wliked@outlook.com)
# 
###############################################################


# set preject name
project (VersionStringCompare)

#TODO : add UNIX for part

# check camke version
cmake_minimum_required(VERSION 2.8)

# The version of this project
set(project_version_major "1")
set(project_version_minor "1")
set(project_version_patch "1")  
set(project_version "${project_version_major}.${project_version_minor}")
set(project_version_full "${project_version}.${project_version_patch}")

# useful environment vaiables
if(WIN32)
    set(target_os_short_name    "win")
    
    if(CMAKE_CL_64) ## check the compiler version.
        set(target_arch_name           "amd64")
        set(system_short_name          "Win64")
        set(extlib_dir_name            ${system_short_name})
        set(extlib_path ${PROJECT_SOURCE_DIR}/extlib/Win64)
    else()
        set(target_arch_name           "x86")
        set(system_short_name          "Win32")
        set(extlib_dir_name            ${system_short_name})
        set(extlib_path ${PROJECT_SOURCE_DIR}/extlib/Win32)
    endif(CMAKE_CL_64)
    
endif(WIN32)

# set up install path
set(install_dir_name output-${project_version_full}-${system_short_name}-${CMAKE_BUILD_TYPE})
set(CMAKE_INSTALL_PREFIX ${PROJECT_SOURCE_DIR}/build/${install_dir_name})

# external header file
include_directories(${PROJECT_SOURCE_DIR}/extlib/include)

# external library file
link_directories(${PROJECT_SOURCE_DIR}/extlib/WIN64/lib)

# set sorce file for executable binary
aux_source_directory(${PROJECT_SOURCE_DIR}/src/ SRC_LIST)

# add executalbe target binary
add_executable(ver_str_comp ${SRC_LIST})

# installation
install(TARGETS ver_str_comp DESTINATION bin/)