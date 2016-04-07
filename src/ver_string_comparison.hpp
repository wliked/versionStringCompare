/******************************************
*
* Copyright (c) 2016 : wang liang
* License : Distributed under the GNU General Public License
* created on : 4/02/2016,  by wang liang (wliked@outlook.com)
* 
******************************************/

#ifndef VERSTRINGCOMPARISON_H
#define VERSTRINGCOMPARISON_H

#include <vector>
#include <string>
#include <iostream>
#include <algorithm>
#include <ctype.h>

#include "boost/regex.hpp"
#include "boost/algorithm/string/regex.hpp"
#include "boost/algorithm/string.hpp"


/* Represents a version string and gives the ability
 * to perform a smart comparison of it to another version
 * string.  Also can be implicitly converted back to its
 * string representation.
 *
 * This class will encapsulate all of our version string
 * logic, and thus is not unique simply to Comparison or
 * Association code.
 */
class VersionStringHandler
{
public:
    VersionStringHandler(const std::string &dst_ver);
    ~VersionStringHandler();
    int CompareTo(const std::string &dst_ver, bool compareverasstring=false);
    bool CompareByRegex(const std::string &pcre);
    operator std::string const &();
    std::vector<std::string> get_segments();
protected:
    std::string GetAlphaOrNumber(const std::string &value);
    //to decide if f_version is valid hex version, for non ESW SUP, version format is not unified
    //LSI expander fw use hex nubmer as version, the legacy compare logic can't handle it
    //if a version can be take as positive hex(but no pre-fix 0x or surfix h to indicate it's a hex, as the version of expander fw) integer uxspi will 
    //compare it as hex. It won't hurt if it's acturely dec, the compare result can be proved to the same 
    bool ValidHexVersion(const std::string &f_version);
    int CompareToAsHex(const std::string &ver);
    int HexToDec(const std::string &f_hex);
    std::string version_;
    std::vector<std::string> ver_segments_;
};


enum
{
    kGREATERTHAN = 1,
    kEQUALTO = 0,
    kLESSTHAN = -1
};
#endif //VERSTRINGCOMPARISON_H