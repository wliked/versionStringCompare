/******************************************
*
* Copyright (c) 2016 : wang liang
* License : Distributed under the GNU General Public License
* created on : 4/02/2016,  by wang liang (wliked@outlook.com)
* 
******************************************/

#include "ver_string_comparison.hpp"


using namespace std;

VersionStringHandler::VersionStringHandler(const string &ver)
{
    version_ = ver;
    std::transform(version_.begin(),version_.end(),version_.begin(),(int(*)(int))std::tolower);
    string current_segment = "";
    //First we'll segment the string, breaking it apart by non-alphanumeric characters
    for (size_t i = 0; i < version_.length(); i++)
    {
        if (isalnum(version_[i]))
            current_segment+=version_.substr(i,1);
        else
        {
            ver_segments_.push_back(current_segment);
            current_segment = "";
        }

        if ((i+1 >= version_.length()) &&
                (current_segment.length() > 0))
            ver_segments_.push_back(current_segment);
    }
}

VersionStringHandler::~VersionStringHandler()
{

}

vector<string> VersionStringHandler::get_segments()
{
    return ver_segments_;
}

bool VersionStringHandler::ValidHexVersion(const string &f_version)
{
    if (f_version.find_first_not_of("1234567890abcdefABCDEF")==std::string::npos)
    {
        return true;
    }
    else
    {
        return false;
    }
}
int VersionStringHandler::CompareToAsHex(const string &f_ver)
{
    int m_version1=HexToDec(version_);
    int m_version2=HexToDec(f_ver);
    if (m_version1==m_version2)
        return 0;
    else if (m_version1>m_version2)
        return 1;
    else
        return -1;
}
int VersionStringHandler::HexToDec(const string &f_hex)
{
    int index=0;
    int re=0;
    while (index<f_hex.length())
    {
        if (f_hex[index]<='9' && f_hex[index]>='0')
        {
            re *=16;
            re += f_hex[index] -'0';
        }
        else if (f_hex[index]<='f' && f_hex[index]>='a')
        {
            re*=16;
            re+= f_hex[index] -'a'+10;
        }
        else if (f_hex[index]<='F' && f_hex[index]>='A')
        {
            re*=16;
            re+= f_hex[index] -'A'+10;
        }
        else
        {
            return 0;
        }
        index++;
    }
    return re;
}
/* Perform an intelligent version comparison between
* this version string and another version string.
* this works even if the other version string is of
* this same type due to the conversation operator.
*
* 1 -> this version is newer than the given version
* 0 -> the two versions are the same
* -1 -> the given version is newer than this version
*/
int VersionStringHandler::CompareTo(const string &ver, bool compareverasstring)
{
    //If it is an easy match, then we'll make it easy on ourselves.
    string cver = ver;
    std::transform(cver.begin(),cver.end(),cver.begin(),(int(*)(int))std::tolower);
    if (version_.compare(cver) == 0)
        return 0;

    if (compareverasstring)   // This version compare is specially for HDD where A->Z is newer than 0->9
    {
        // which is true in ascii.
        return version_.compare(cver);
    }
    else if (ValidHexVersion(version_) && ValidHexVersion(cver))
    {
        return CompareToAsHex(cver);
    }

    int result = 0;

    VersionStringHandler *tcver = new VersionStringHandler(cver);
    vector<string> g_ver_segments = tcver->get_segments();

    for (size_t i = 0; i < ver_segments_.size(); i++)
    {
        if (i+1 > g_ver_segments.size())
        {
            result = 1;
            break;
        }

        size_t t_segord = ver_segments_.at(i).find_first_not_of("0");
        size_t g_segord = g_ver_segments.at(i).find_first_not_of("0");

        string t_mseg;
        if (t_segord != string::npos)
        {
            t_mseg = ver_segments_.at(i).substr(t_segord, ver_segments_.at(i).length());
        }
        else
        {
            t_mseg = ver_segments_.at(i);
        }

        string g_mseg;
        if (g_segord != string::npos)
        {
            g_mseg = g_ver_segments.at(i).substr(g_segord, g_ver_segments.at(i).length());
        }
        else
        {
            g_mseg = g_ver_segments.at(i);
        }


        string t_run = this->GetAlphaOrNumber(t_mseg);
        t_segord = t_segord+t_run.length();
        string g_run = this->GetAlphaOrNumber(g_mseg);
        g_segord = g_segord+g_run.length();

        while (t_run.length() > 0 || g_run.length() > 0)
        {
            if (t_run.length() > 0 && g_run.length() < 1)
            {
                result = 1;
                break;
            }
            else if (g_run.length() > 0 && t_run.length() < 1)
            {
                result = -1;
                break;
            }

            if (isalpha(t_run[0]) && isalpha(g_run[0]))
            {
                result = t_run.compare(g_run);
                if (result != 0)
                    break;
            }
            else if (isdigit(t_run[0]) && isdigit(g_run[0]))
            {
                if (atoi(t_run.c_str()) > atoi(g_run.c_str()))
                {
                    result = 1;
                    break;
                }
                else if (atoi(t_run.c_str()) < atoi(g_run.c_str()))
                {
                    result = -1;
                    break;
                }
                else
                    result = 0;
            }
            else     //we favor numbers over letters
            {
                if (isdigit(t_run[0]) && !isdigit(g_run[0]))
                {
                    result = 1;
                    break;
                }
                else if (isdigit(g_run[0]) && !isdigit(t_run[0]))
                {
                    result = -1;
                    break;
                }
            }

            //if we get here, we need to get the next run part of this segment
            t_mseg = ver_segments_.at(i).substr(t_segord, ver_segments_.at(i).length());
            if (g_segord > ver_segments_.at(i).length())
                break;
            g_mseg = g_ver_segments.at(i).substr(g_segord, ver_segments_.at(i).length());

            t_run = this->GetAlphaOrNumber(t_mseg);
            t_segord = t_segord+t_run.length();
            g_run = this->GetAlphaOrNumber(g_mseg);
            g_segord = g_segord+g_run.length();
        }
        if (result != 0) //if we made a decision in the while loop then we'll stop
            break;
    }

    //if we are the same up to this point, and the given version has more
    //segments than this version, then the given version wins.
    if (result == 0 && (ver_segments_.size() < g_ver_segments.size()))
        result = -1;

    delete tcver;
    return result;
}

/* Compare a version string to a perl-style regular expression
* for a simple match.
*/
bool VersionStringHandler::CompareByRegex(const string &pcre)
{
    boost::regex stre(pcre);
    if (boost::regex_match(version_, stre))
        return true;
    else
        return false;
}

/* Given a string this method will determine whether the first
* character is a number or an alpha, and will collect the characters
* to the right of that character that are of the same type (alpha/number)
* stopping at the first one that isn't and returning the contents up to
* that point.
*/
string VersionStringHandler::GetAlphaOrNumber(const string &val)
{
    if (val.length() < 1)
        return "";

    string r_str = "";

    if (isalpha(val[0]))
    {
        for (size_t i = 0; i < val.length(); i++)
        {
            if (isalpha(val[i]))
                r_str+=val.substr(i,1);
            else
                break;
        }
    }
    else if (isdigit(val[0]))
    {
        for (size_t i = 0; i < val.length(); i++)
        {
            if (isdigit(val[i]))
                r_str+=val.substr(i,1);
            else
                break;
        }
    }
    else
        return "";
    return r_str;
}

/* Give the VersionStringHandler object the ability to
* simply return the string representation if that
* is what is desired.
*/
VersionStringHandler::operator string const &()
{
    return version_;
}
