/******************************************
*
* Copyright (c) 2016 : wang liang
* License : Distributed under the GNU General Public License
* created on : 4/02/2016,  by wang liang (wliked@outlook.com)
* 
******************************************/

#include <string>
#include "ver_string_comparison.hpp"

using namespace std;

int main(int argc, char **argv)
{
      string source_str = "16.02.a";
      string target_str = "15.03.d";
      VersionStringHandler *ver_handler = new VersionStringHandler(source_str);
      int compare_result = ver_handler->CompareTo(target_str);

      switch (compare_result)
      {
	 case 1 :
	  	 cout << "source version string is greater than target string." << endl;
	        break;
	 case 0 :
	  	 cout << "source version string is equal with target string." << endl;
	        break;
	 case -1 :
	  	 cout << "source version string is lower than target string." << endl;
	        break;
	 default :
	  	 break;
       }  
       delete ver_handler;
       return 0;
}
