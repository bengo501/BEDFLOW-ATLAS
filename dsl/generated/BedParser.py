# Generated from grammar/Bed.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,121,620,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,
        7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,
        13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,
        20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,
        26,2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,1,
        0,4,0,68,8,0,11,0,12,0,69,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,3,1,84,8,1,1,2,1,2,1,2,4,2,89,8,2,11,2,12,2,90,1,2,1,2,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,4,3,131,8,3,11,3,12,3,132,1,3,1,3,3,3,137,8,3,1,
        4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        4,1,4,1,4,1,4,3,4,159,8,4,1,5,1,5,1,5,4,5,164,8,5,11,5,12,5,165,
        1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,
        1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,6,195,8,6,1,7,1,7,
        1,8,1,8,1,8,4,8,202,8,8,11,8,12,8,203,1,8,1,8,1,9,1,9,1,9,1,9,1,
        9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,
        9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,
        9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,3,
        9,260,8,9,1,10,1,10,1,11,1,11,1,11,4,11,267,8,11,11,11,12,11,268,
        1,11,1,11,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,
        1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,
        1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,
        1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,
        1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,
        1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,
        1,12,1,12,4,12,351,8,12,11,12,12,12,352,1,12,1,12,3,12,357,8,12,
        1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,
        1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,
        1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,1,13,
        1,13,1,13,1,13,1,13,1,13,3,13,403,8,13,1,14,1,14,1,15,1,15,1,15,
        4,15,410,8,15,11,15,12,15,411,1,15,1,15,1,16,1,16,1,16,1,16,1,16,
        1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,
        1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,
        1,16,1,16,1,16,3,16,450,8,16,1,17,1,17,1,17,5,17,455,8,17,10,17,
        12,17,458,9,17,1,18,1,18,1,19,1,19,1,20,1,20,1,20,4,20,467,8,20,
        11,20,12,20,468,1,20,1,20,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,
        1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,
        1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,3,21,505,
        8,21,1,22,1,22,1,23,1,23,1,23,4,23,512,8,23,11,23,12,23,513,1,23,
        1,23,1,24,1,24,1,24,1,24,1,24,1,25,1,25,1,26,1,26,1,26,4,26,528,
        8,26,11,26,12,26,529,1,26,1,26,1,27,1,27,1,27,1,27,1,27,1,28,1,28,
        1,29,1,29,1,29,4,29,544,8,29,11,29,12,29,545,1,29,1,29,1,30,1,30,
        1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,
        1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,1,30,3,30,576,
        8,30,1,31,1,31,1,31,4,31,581,8,31,11,31,12,31,582,1,31,1,31,1,32,
        1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,
        1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,1,32,
        1,32,1,32,1,32,1,32,3,32,618,8,32,1,32,0,0,33,0,2,4,6,8,10,12,14,
        16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,
        60,62,64,0,8,2,0,25,27,117,117,2,0,40,42,117,117,2,0,67,67,117,117,
        2,0,79,80,117,117,3,0,27,27,81,81,117,117,2,0,90,91,117,117,2,0,
        94,96,117,117,2,0,99,100,117,117,684,0,67,1,0,0,0,2,83,1,0,0,0,4,
        85,1,0,0,0,6,136,1,0,0,0,8,158,1,0,0,0,10,160,1,0,0,0,12,194,1,0,
        0,0,14,196,1,0,0,0,16,198,1,0,0,0,18,259,1,0,0,0,20,261,1,0,0,0,
        22,263,1,0,0,0,24,356,1,0,0,0,26,402,1,0,0,0,28,404,1,0,0,0,30,406,
        1,0,0,0,32,449,1,0,0,0,34,451,1,0,0,0,36,459,1,0,0,0,38,461,1,0,
        0,0,40,463,1,0,0,0,42,504,1,0,0,0,44,506,1,0,0,0,46,508,1,0,0,0,
        48,517,1,0,0,0,50,522,1,0,0,0,52,524,1,0,0,0,54,533,1,0,0,0,56,538,
        1,0,0,0,58,540,1,0,0,0,60,575,1,0,0,0,62,577,1,0,0,0,64,617,1,0,
        0,0,66,68,3,2,1,0,67,66,1,0,0,0,68,69,1,0,0,0,69,67,1,0,0,0,69,70,
        1,0,0,0,70,71,1,0,0,0,71,72,5,0,0,1,72,1,1,0,0,0,73,84,3,4,2,0,74,
        84,3,10,5,0,75,84,3,16,8,0,76,84,3,22,11,0,77,84,3,30,15,0,78,84,
        3,40,20,0,79,84,3,46,23,0,80,84,3,52,26,0,81,84,3,58,29,0,82,84,
        3,62,31,0,83,73,1,0,0,0,83,74,1,0,0,0,83,75,1,0,0,0,83,76,1,0,0,
        0,83,77,1,0,0,0,83,78,1,0,0,0,83,79,1,0,0,0,83,80,1,0,0,0,83,81,
        1,0,0,0,83,82,1,0,0,0,84,3,1,0,0,0,85,86,5,1,0,0,86,88,5,2,0,0,87,
        89,3,6,3,0,88,87,1,0,0,0,89,90,1,0,0,0,90,88,1,0,0,0,90,91,1,0,0,
        0,91,92,1,0,0,0,92,93,5,3,0,0,93,5,1,0,0,0,94,95,5,4,0,0,95,96,5,
        5,0,0,96,97,5,114,0,0,97,98,5,116,0,0,98,137,5,6,0,0,99,100,5,7,
        0,0,100,101,5,5,0,0,101,102,5,114,0,0,102,103,5,116,0,0,103,137,
        5,6,0,0,104,105,5,8,0,0,105,106,5,5,0,0,106,107,5,114,0,0,107,108,
        5,116,0,0,108,137,5,6,0,0,109,110,5,9,0,0,110,111,5,5,0,0,111,112,
        5,114,0,0,112,113,5,116,0,0,113,137,5,6,0,0,114,115,5,10,0,0,115,
        116,5,5,0,0,116,117,5,117,0,0,117,137,5,6,0,0,118,119,5,11,0,0,119,
        120,5,5,0,0,120,121,5,114,0,0,121,122,5,116,0,0,122,137,5,6,0,0,
        123,124,5,12,0,0,124,125,5,5,0,0,125,126,5,117,0,0,126,137,5,6,0,
        0,127,128,5,13,0,0,128,130,5,2,0,0,129,131,3,8,4,0,130,129,1,0,0,
        0,131,132,1,0,0,0,132,130,1,0,0,0,132,133,1,0,0,0,133,134,1,0,0,
        0,134,135,5,3,0,0,135,137,1,0,0,0,136,94,1,0,0,0,136,99,1,0,0,0,
        136,104,1,0,0,0,136,109,1,0,0,0,136,114,1,0,0,0,136,118,1,0,0,0,
        136,123,1,0,0,0,136,127,1,0,0,0,137,7,1,0,0,0,138,139,5,14,0,0,139,
        140,5,5,0,0,140,141,5,118,0,0,141,159,5,6,0,0,142,143,5,15,0,0,143,
        144,5,5,0,0,144,145,5,118,0,0,145,159,5,6,0,0,146,147,5,16,0,0,147,
        148,5,5,0,0,148,149,5,118,0,0,149,159,5,6,0,0,150,151,5,17,0,0,151,
        152,5,5,0,0,152,153,5,118,0,0,153,159,5,6,0,0,154,155,5,18,0,0,155,
        156,5,5,0,0,156,157,5,118,0,0,157,159,5,6,0,0,158,138,1,0,0,0,158,
        142,1,0,0,0,158,146,1,0,0,0,158,150,1,0,0,0,158,154,1,0,0,0,159,
        9,1,0,0,0,160,161,5,19,0,0,161,163,5,2,0,0,162,164,3,12,6,0,163,
        162,1,0,0,0,164,165,1,0,0,0,165,163,1,0,0,0,165,166,1,0,0,0,166,
        167,1,0,0,0,167,168,5,3,0,0,168,11,1,0,0,0,169,170,5,20,0,0,170,
        171,5,5,0,0,171,172,3,14,7,0,172,173,5,6,0,0,173,195,1,0,0,0,174,
        175,5,21,0,0,175,176,5,5,0,0,176,177,3,14,7,0,177,178,5,6,0,0,178,
        195,1,0,0,0,179,180,5,22,0,0,180,181,5,5,0,0,181,182,5,114,0,0,182,
        183,5,116,0,0,183,195,5,6,0,0,184,185,5,23,0,0,185,186,5,5,0,0,186,
        187,5,114,0,0,187,188,5,116,0,0,188,195,5,6,0,0,189,190,5,24,0,0,
        190,191,5,5,0,0,191,192,5,114,0,0,192,193,5,116,0,0,193,195,5,6,
        0,0,194,169,1,0,0,0,194,174,1,0,0,0,194,179,1,0,0,0,194,184,1,0,
        0,0,194,189,1,0,0,0,195,13,1,0,0,0,196,197,7,0,0,0,197,15,1,0,0,
        0,198,199,5,28,0,0,199,201,5,2,0,0,200,202,3,18,9,0,201,200,1,0,
        0,0,202,203,1,0,0,0,203,201,1,0,0,0,203,204,1,0,0,0,204,205,1,0,
        0,0,205,206,5,3,0,0,206,17,1,0,0,0,207,208,5,29,0,0,208,209,5,5,
        0,0,209,210,3,20,10,0,210,211,5,6,0,0,211,260,1,0,0,0,212,213,5,
        4,0,0,213,214,5,5,0,0,214,215,5,114,0,0,215,216,5,116,0,0,216,260,
        5,6,0,0,217,218,5,30,0,0,218,219,5,5,0,0,219,220,5,114,0,0,220,260,
        5,6,0,0,221,222,5,31,0,0,222,223,5,5,0,0,223,224,5,114,0,0,224,260,
        5,6,0,0,225,226,5,32,0,0,226,227,5,5,0,0,227,228,5,114,0,0,228,229,
        5,116,0,0,229,260,5,6,0,0,230,231,5,33,0,0,231,232,5,5,0,0,232,233,
        5,114,0,0,233,234,5,116,0,0,234,260,5,6,0,0,235,236,5,34,0,0,236,
        237,5,5,0,0,237,238,5,114,0,0,238,260,5,6,0,0,239,240,5,35,0,0,240,
        241,5,5,0,0,241,242,5,114,0,0,242,260,5,6,0,0,243,244,5,36,0,0,244,
        245,5,5,0,0,245,246,5,114,0,0,246,260,5,6,0,0,247,248,5,37,0,0,248,
        249,5,5,0,0,249,250,5,114,0,0,250,260,5,6,0,0,251,252,5,38,0,0,252,
        253,5,5,0,0,253,254,5,114,0,0,254,260,5,6,0,0,255,256,5,39,0,0,256,
        257,5,5,0,0,257,258,5,114,0,0,258,260,5,6,0,0,259,207,1,0,0,0,259,
        212,1,0,0,0,259,217,1,0,0,0,259,221,1,0,0,0,259,225,1,0,0,0,259,
        230,1,0,0,0,259,235,1,0,0,0,259,239,1,0,0,0,259,243,1,0,0,0,259,
        247,1,0,0,0,259,251,1,0,0,0,259,255,1,0,0,0,260,19,1,0,0,0,261,262,
        7,1,0,0,262,21,1,0,0,0,263,264,5,43,0,0,264,266,5,2,0,0,265,267,
        3,24,12,0,266,265,1,0,0,0,267,268,1,0,0,0,268,266,1,0,0,0,268,269,
        1,0,0,0,269,270,1,0,0,0,270,271,5,3,0,0,271,23,1,0,0,0,272,273,5,
        44,0,0,273,274,5,5,0,0,274,275,3,28,14,0,275,276,5,6,0,0,276,357,
        1,0,0,0,277,278,5,45,0,0,278,279,5,5,0,0,279,280,5,114,0,0,280,281,
        5,116,0,0,281,357,5,6,0,0,282,283,5,46,0,0,283,284,5,5,0,0,284,285,
        5,114,0,0,285,357,5,6,0,0,286,287,5,47,0,0,287,288,5,5,0,0,288,289,
        5,114,0,0,289,357,5,6,0,0,290,291,5,48,0,0,291,292,5,5,0,0,292,293,
        5,114,0,0,293,357,5,6,0,0,294,295,5,49,0,0,295,296,5,5,0,0,296,297,
        5,114,0,0,297,298,5,116,0,0,298,357,5,6,0,0,299,300,5,50,0,0,300,
        301,5,5,0,0,301,302,5,114,0,0,302,303,5,116,0,0,303,357,5,6,0,0,
        304,305,5,51,0,0,305,306,5,5,0,0,306,307,5,114,0,0,307,308,5,116,
        0,0,308,357,5,6,0,0,309,310,5,52,0,0,310,311,5,5,0,0,311,312,5,114,
        0,0,312,313,5,116,0,0,313,357,5,6,0,0,314,315,5,53,0,0,315,316,5,
        5,0,0,316,317,5,114,0,0,317,357,5,6,0,0,318,319,5,54,0,0,319,320,
        5,5,0,0,320,321,5,114,0,0,321,357,5,6,0,0,322,323,5,55,0,0,323,324,
        5,5,0,0,324,325,5,118,0,0,325,357,5,6,0,0,326,327,5,56,0,0,327,328,
        5,5,0,0,328,329,5,114,0,0,329,330,5,116,0,0,330,357,5,6,0,0,331,
        332,5,57,0,0,332,333,5,5,0,0,333,334,5,114,0,0,334,357,5,6,0,0,335,
        336,5,58,0,0,336,337,5,5,0,0,337,338,5,114,0,0,338,357,5,6,0,0,339,
        340,5,59,0,0,340,341,5,5,0,0,341,342,5,114,0,0,342,357,5,6,0,0,343,
        344,5,60,0,0,344,345,5,5,0,0,345,346,5,118,0,0,346,357,5,6,0,0,347,
        348,5,61,0,0,348,350,5,2,0,0,349,351,3,26,13,0,350,349,1,0,0,0,351,
        352,1,0,0,0,352,350,1,0,0,0,352,353,1,0,0,0,353,354,1,0,0,0,354,
        355,5,3,0,0,355,357,1,0,0,0,356,272,1,0,0,0,356,277,1,0,0,0,356,
        282,1,0,0,0,356,286,1,0,0,0,356,290,1,0,0,0,356,294,1,0,0,0,356,
        299,1,0,0,0,356,304,1,0,0,0,356,309,1,0,0,0,356,314,1,0,0,0,356,
        318,1,0,0,0,356,322,1,0,0,0,356,326,1,0,0,0,356,331,1,0,0,0,356,
        335,1,0,0,0,356,339,1,0,0,0,356,343,1,0,0,0,356,347,1,0,0,0,357,
        25,1,0,0,0,358,359,5,62,0,0,359,360,5,5,0,0,360,361,5,114,0,0,361,
        362,5,116,0,0,362,403,5,6,0,0,363,364,5,63,0,0,364,365,5,5,0,0,365,
        366,5,114,0,0,366,403,5,6,0,0,367,368,5,45,0,0,368,369,5,5,0,0,369,
        370,5,114,0,0,370,371,5,116,0,0,371,403,5,6,0,0,372,373,5,64,0,0,
        373,374,5,5,0,0,374,375,5,114,0,0,375,403,5,6,0,0,376,377,5,48,0,
        0,377,378,5,5,0,0,378,379,5,114,0,0,379,403,5,6,0,0,380,381,5,35,
        0,0,381,382,5,5,0,0,382,383,5,114,0,0,383,403,5,6,0,0,384,385,5,
        34,0,0,385,386,5,5,0,0,386,387,5,114,0,0,387,403,5,6,0,0,388,389,
        5,65,0,0,389,390,5,5,0,0,390,391,5,114,0,0,391,392,5,116,0,0,392,
        403,5,6,0,0,393,394,5,66,0,0,394,395,5,5,0,0,395,396,5,114,0,0,396,
        397,5,116,0,0,397,403,5,6,0,0,398,399,5,39,0,0,399,400,5,5,0,0,400,
        401,5,114,0,0,401,403,5,6,0,0,402,358,1,0,0,0,402,363,1,0,0,0,402,
        367,1,0,0,0,402,372,1,0,0,0,402,376,1,0,0,0,402,380,1,0,0,0,402,
        384,1,0,0,0,402,388,1,0,0,0,402,393,1,0,0,0,402,398,1,0,0,0,403,
        27,1,0,0,0,404,405,7,2,0,0,405,29,1,0,0,0,406,407,5,68,0,0,407,409,
        5,2,0,0,408,410,3,32,16,0,409,408,1,0,0,0,410,411,1,0,0,0,411,409,
        1,0,0,0,411,412,1,0,0,0,412,413,1,0,0,0,413,414,5,3,0,0,414,31,1,
        0,0,0,415,416,5,69,0,0,416,417,5,5,0,0,417,418,5,70,0,0,418,419,
        3,34,17,0,419,420,5,71,0,0,420,421,5,6,0,0,421,450,1,0,0,0,422,423,
        5,72,0,0,423,424,5,5,0,0,424,425,5,117,0,0,425,450,5,6,0,0,426,427,
        5,73,0,0,427,428,5,5,0,0,428,429,5,114,0,0,429,450,5,6,0,0,430,431,
        5,74,0,0,431,432,5,5,0,0,432,433,3,36,18,0,433,434,5,6,0,0,434,450,
        1,0,0,0,435,436,5,75,0,0,436,437,5,5,0,0,437,438,3,38,19,0,438,439,
        5,6,0,0,439,450,1,0,0,0,440,441,5,76,0,0,441,442,5,5,0,0,442,443,
        5,118,0,0,443,450,5,6,0,0,444,445,5,77,0,0,445,446,5,5,0,0,446,447,
        5,114,0,0,447,448,5,116,0,0,448,450,5,6,0,0,449,415,1,0,0,0,449,
        422,1,0,0,0,449,426,1,0,0,0,449,430,1,0,0,0,449,435,1,0,0,0,449,
        440,1,0,0,0,449,444,1,0,0,0,450,33,1,0,0,0,451,456,5,117,0,0,452,
        453,5,78,0,0,453,455,5,117,0,0,454,452,1,0,0,0,455,458,1,0,0,0,456,
        454,1,0,0,0,456,457,1,0,0,0,457,35,1,0,0,0,458,456,1,0,0,0,459,460,
        7,3,0,0,460,37,1,0,0,0,461,462,7,4,0,0,462,39,1,0,0,0,463,464,5,
        82,0,0,464,466,5,2,0,0,465,467,3,42,21,0,466,465,1,0,0,0,467,468,
        1,0,0,0,468,466,1,0,0,0,468,469,1,0,0,0,469,470,1,0,0,0,470,471,
        5,3,0,0,471,41,1,0,0,0,472,473,5,83,0,0,473,474,5,5,0,0,474,475,
        3,44,22,0,475,476,5,6,0,0,476,505,1,0,0,0,477,478,5,84,0,0,478,479,
        5,5,0,0,479,480,5,114,0,0,480,481,5,116,0,0,481,505,5,6,0,0,482,
        483,5,85,0,0,483,484,5,5,0,0,484,485,5,114,0,0,485,486,5,116,0,0,
        486,505,5,6,0,0,487,488,5,86,0,0,488,489,5,5,0,0,489,490,5,114,0,
        0,490,491,5,116,0,0,491,505,5,6,0,0,492,493,5,87,0,0,493,494,5,5,
        0,0,494,495,5,114,0,0,495,505,5,6,0,0,496,497,5,88,0,0,497,498,5,
        5,0,0,498,499,5,114,0,0,499,505,5,6,0,0,500,501,5,89,0,0,501,502,
        5,5,0,0,502,503,5,118,0,0,503,505,5,6,0,0,504,472,1,0,0,0,504,477,
        1,0,0,0,504,482,1,0,0,0,504,487,1,0,0,0,504,492,1,0,0,0,504,496,
        1,0,0,0,504,500,1,0,0,0,505,43,1,0,0,0,506,507,7,5,0,0,507,45,1,
        0,0,0,508,509,5,92,0,0,509,511,5,2,0,0,510,512,3,48,24,0,511,510,
        1,0,0,0,512,513,1,0,0,0,513,511,1,0,0,0,513,514,1,0,0,0,514,515,
        1,0,0,0,515,516,5,3,0,0,516,47,1,0,0,0,517,518,5,93,0,0,518,519,
        5,5,0,0,519,520,3,50,25,0,520,521,5,6,0,0,521,49,1,0,0,0,522,523,
        7,6,0,0,523,51,1,0,0,0,524,525,5,97,0,0,525,527,5,2,0,0,526,528,
        3,54,27,0,527,526,1,0,0,0,528,529,1,0,0,0,529,527,1,0,0,0,529,530,
        1,0,0,0,530,531,1,0,0,0,531,532,5,3,0,0,532,53,1,0,0,0,533,534,5,
        98,0,0,534,535,5,5,0,0,535,536,3,56,28,0,536,537,5,6,0,0,537,55,
        1,0,0,0,538,539,7,7,0,0,539,57,1,0,0,0,540,541,5,101,0,0,541,543,
        5,2,0,0,542,544,3,60,30,0,543,542,1,0,0,0,544,545,1,0,0,0,545,543,
        1,0,0,0,545,546,1,0,0,0,546,547,1,0,0,0,547,548,5,3,0,0,548,59,1,
        0,0,0,549,550,5,102,0,0,550,551,5,5,0,0,551,552,5,118,0,0,552,576,
        5,6,0,0,553,554,5,103,0,0,554,555,5,5,0,0,555,556,5,114,0,0,556,
        557,5,116,0,0,557,576,5,6,0,0,558,559,5,104,0,0,559,560,5,5,0,0,
        560,561,5,117,0,0,561,576,5,6,0,0,562,563,5,105,0,0,563,564,5,5,
        0,0,564,565,5,114,0,0,565,566,5,116,0,0,566,576,5,6,0,0,567,568,
        5,106,0,0,568,569,5,5,0,0,569,570,5,118,0,0,570,576,5,6,0,0,571,
        572,5,107,0,0,572,573,5,5,0,0,573,574,5,118,0,0,574,576,5,6,0,0,
        575,549,1,0,0,0,575,553,1,0,0,0,575,558,1,0,0,0,575,562,1,0,0,0,
        575,567,1,0,0,0,575,571,1,0,0,0,576,61,1,0,0,0,577,578,5,108,0,0,
        578,580,5,2,0,0,579,581,3,64,32,0,580,579,1,0,0,0,581,582,1,0,0,
        0,582,580,1,0,0,0,582,583,1,0,0,0,583,584,1,0,0,0,584,585,5,3,0,
        0,585,63,1,0,0,0,586,587,5,109,0,0,587,588,5,5,0,0,588,589,5,114,
        0,0,589,590,5,116,0,0,590,618,5,6,0,0,591,592,5,110,0,0,592,593,
        5,5,0,0,593,594,5,114,0,0,594,595,5,116,0,0,595,618,5,6,0,0,596,
        597,5,31,0,0,597,598,5,5,0,0,598,599,5,114,0,0,599,618,5,6,0,0,600,
        601,5,111,0,0,601,602,5,5,0,0,602,603,5,114,0,0,603,618,5,6,0,0,
        604,605,5,112,0,0,605,606,5,5,0,0,606,607,5,114,0,0,607,618,5,6,
        0,0,608,609,5,113,0,0,609,610,5,5,0,0,610,611,5,114,0,0,611,612,
        5,116,0,0,612,618,5,6,0,0,613,614,5,39,0,0,614,615,5,5,0,0,615,616,
        5,114,0,0,616,618,5,6,0,0,617,586,1,0,0,0,617,591,1,0,0,0,617,596,
        1,0,0,0,617,600,1,0,0,0,617,604,1,0,0,0,617,608,1,0,0,0,617,613,
        1,0,0,0,618,65,1,0,0,0,25,69,83,90,132,136,158,165,194,203,259,268,
        352,356,402,411,449,456,468,504,513,529,545,575,582,617
    ]

class BedParser ( Parser ):

    grammarFileName = "Bed.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'bed'", "'{'", "'}'", "'diameter'", "'='", 
                     "';'", "'height'", "'wall_thickness'", "'clearance'", 
                     "'material'", "'roughness'", "'internal_cylinder_mode'", 
                     "'visibility'", "'show_outer_cylinder'", "'show_internal_cylinder'", 
                     "'show_particles'", "'show_boolean_tools'", "'export_boolean_tools'", 
                     "'lids'", "'top_type'", "'bottom_type'", "'top_thickness'", 
                     "'bottom_thickness'", "'seal_clearance'", "'flat'", 
                     "'hemispherical'", "'none'", "'particles'", "'kind'", 
                     "'count'", "'target_porosity'", "'density'", "'mass'", 
                     "'restitution'", "'friction'", "'rolling_friction'", 
                     "'linear_damping'", "'angular_damping'", "'seed'", 
                     "'sphere'", "'cube'", "'cylinder'", "'packing'", "'method'", 
                     "'gravity'", "'substeps'", "'iterations'", "'damping'", 
                     "'rest_velocity'", "'max_time'", "'collision_margin'", 
                     "'gap'", "'random_seed'", "'max_placement_attempts'", 
                     "'strict_validation'", "'step_x'", "'mesh_segmentos'", 
                     "'sphere_lat'", "'sphere_lon'", "'use_legacy_drop'", 
                     "'dem'", "'time_step'", "'steps'", "'stiffness'", "'settle_threshold'", 
                     "'max_velocity_threshold'", "'rigid_body'", "'export'", 
                     "'formats'", "'['", "']'", "'units'", "'scale'", "'wall_mode'", 
                     "'fluid_mode'", "'manifold_check'", "'merge_distance'", 
                     "','", "'surface'", "'solid'", "'cavity'", "'cfd'", 
                     "'regime'", "'inlet_velocity'", "'fluid_density'", 
                     "'fluid_viscosity'", "'max_iterations'", "'convergence_criteria'", 
                     "'write_fields'", "'laminar'", "'turbulent_rans'", 
                     "'geometry'", "'mode'", "'full_3d'", "'pseudo_2d_thin_slice'", 
                     "'pseudo_2d_statistical'", "'generation'", "'backend'", 
                     "'python_engine'", "'blender'", "'slice'", "'enabled'", 
                     "'thickness'", "'axis'", "'position'", "'keep_only_intersecting_particles'", 
                     "'preserve_original_packing'", "'statistical_2d'", 
                     "'domain_width'", "'domain_height'", "'tolerance'", 
                     "'max_attempts'", "'slice_thickness'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "NUMBER", "INTEGER", "UNIT", 
                      "STRING", "BOOLEAN", "WS", "COMMENT", "BLOCK_COMMENT" ]

    RULE_bedFile = 0
    RULE_section = 1
    RULE_bedSection = 2
    RULE_bedProperty = 3
    RULE_visibilityProperty = 4
    RULE_lidsSection = 5
    RULE_lidsProperty = 6
    RULE_lidType = 7
    RULE_particlesSection = 8
    RULE_particlesProperty = 9
    RULE_particleKind = 10
    RULE_packingSection = 11
    RULE_packingProperty = 12
    RULE_demProperty = 13
    RULE_packingMethod = 14
    RULE_exportSection = 15
    RULE_exportProperty = 16
    RULE_formatList = 17
    RULE_wallMode = 18
    RULE_fluidMode = 19
    RULE_cfdSection = 20
    RULE_cfdProperty = 21
    RULE_cfdRegime = 22
    RULE_geometrySection = 23
    RULE_geometryProperty = 24
    RULE_geometryMode = 25
    RULE_generationSection = 26
    RULE_generationProperty = 27
    RULE_generationBackend = 28
    RULE_sliceSection = 29
    RULE_sliceProperty = 30
    RULE_statistical2dSection = 31
    RULE_statistical2dProperty = 32

    ruleNames =  [ "bedFile", "section", "bedSection", "bedProperty", "visibilityProperty", 
                   "lidsSection", "lidsProperty", "lidType", "particlesSection", 
                   "particlesProperty", "particleKind", "packingSection", 
                   "packingProperty", "demProperty", "packingMethod", "exportSection", 
                   "exportProperty", "formatList", "wallMode", "fluidMode", 
                   "cfdSection", "cfdProperty", "cfdRegime", "geometrySection", 
                   "geometryProperty", "geometryMode", "generationSection", 
                   "generationProperty", "generationBackend", "sliceSection", 
                   "sliceProperty", "statistical2dSection", "statistical2dProperty" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    T__42=43
    T__43=44
    T__44=45
    T__45=46
    T__46=47
    T__47=48
    T__48=49
    T__49=50
    T__50=51
    T__51=52
    T__52=53
    T__53=54
    T__54=55
    T__55=56
    T__56=57
    T__57=58
    T__58=59
    T__59=60
    T__60=61
    T__61=62
    T__62=63
    T__63=64
    T__64=65
    T__65=66
    T__66=67
    T__67=68
    T__68=69
    T__69=70
    T__70=71
    T__71=72
    T__72=73
    T__73=74
    T__74=75
    T__75=76
    T__76=77
    T__77=78
    T__78=79
    T__79=80
    T__80=81
    T__81=82
    T__82=83
    T__83=84
    T__84=85
    T__85=86
    T__86=87
    T__87=88
    T__88=89
    T__89=90
    T__90=91
    T__91=92
    T__92=93
    T__93=94
    T__94=95
    T__95=96
    T__96=97
    T__97=98
    T__98=99
    T__99=100
    T__100=101
    T__101=102
    T__102=103
    T__103=104
    T__104=105
    T__105=106
    T__106=107
    T__107=108
    T__108=109
    T__109=110
    T__110=111
    T__111=112
    T__112=113
    NUMBER=114
    INTEGER=115
    UNIT=116
    STRING=117
    BOOLEAN=118
    WS=119
    COMMENT=120
    BLOCK_COMMENT=121

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class BedFileContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(BedParser.EOF, 0)

        def section(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.SectionContext)
            else:
                return self.getTypedRuleContext(BedParser.SectionContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_bedFile

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedFile" ):
                listener.enterBedFile(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedFile" ):
                listener.exitBedFile(self)




    def bedFile(self):

        localctx = BedParser.BedFileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_bedFile)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 66
                self.section()
                self.state = 69 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 8796361981954) != 0) or ((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & 1108655226881) != 0)):
                    break

            self.state = 71
            self.match(BedParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def bedSection(self):
            return self.getTypedRuleContext(BedParser.BedSectionContext,0)


        def lidsSection(self):
            return self.getTypedRuleContext(BedParser.LidsSectionContext,0)


        def particlesSection(self):
            return self.getTypedRuleContext(BedParser.ParticlesSectionContext,0)


        def packingSection(self):
            return self.getTypedRuleContext(BedParser.PackingSectionContext,0)


        def exportSection(self):
            return self.getTypedRuleContext(BedParser.ExportSectionContext,0)


        def cfdSection(self):
            return self.getTypedRuleContext(BedParser.CfdSectionContext,0)


        def geometrySection(self):
            return self.getTypedRuleContext(BedParser.GeometrySectionContext,0)


        def generationSection(self):
            return self.getTypedRuleContext(BedParser.GenerationSectionContext,0)


        def sliceSection(self):
            return self.getTypedRuleContext(BedParser.SliceSectionContext,0)


        def statistical2dSection(self):
            return self.getTypedRuleContext(BedParser.Statistical2dSectionContext,0)


        def getRuleIndex(self):
            return BedParser.RULE_section

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSection" ):
                listener.enterSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSection" ):
                listener.exitSection(self)




    def section(self):

        localctx = BedParser.SectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_section)
        try:
            self.state = 83
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 73
                self.bedSection()
                pass
            elif token in [19]:
                self.enterOuterAlt(localctx, 2)
                self.state = 74
                self.lidsSection()
                pass
            elif token in [28]:
                self.enterOuterAlt(localctx, 3)
                self.state = 75
                self.particlesSection()
                pass
            elif token in [43]:
                self.enterOuterAlt(localctx, 4)
                self.state = 76
                self.packingSection()
                pass
            elif token in [68]:
                self.enterOuterAlt(localctx, 5)
                self.state = 77
                self.exportSection()
                pass
            elif token in [82]:
                self.enterOuterAlt(localctx, 6)
                self.state = 78
                self.cfdSection()
                pass
            elif token in [92]:
                self.enterOuterAlt(localctx, 7)
                self.state = 79
                self.geometrySection()
                pass
            elif token in [97]:
                self.enterOuterAlt(localctx, 8)
                self.state = 80
                self.generationSection()
                pass
            elif token in [101]:
                self.enterOuterAlt(localctx, 9)
                self.state = 81
                self.sliceSection()
                pass
            elif token in [108]:
                self.enterOuterAlt(localctx, 10)
                self.state = 82
                self.statistical2dSection()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BedSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def bedProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.BedPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.BedPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_bedSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedSection" ):
                listener.enterBedSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedSection" ):
                listener.exitBedSection(self)




    def bedSection(self):

        localctx = BedParser.BedSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_bedSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(BedParser.T__0)
            self.state = 86
            self.match(BedParser.T__1)
            self.state = 88 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 87
                self.bedProperty()
                self.state = 90 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 16272) != 0)):
                    break

            self.state = 92
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BedPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_bedProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class BedWallThicknessContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedWallThickness" ):
                listener.enterBedWallThickness(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedWallThickness" ):
                listener.exitBedWallThickness(self)


    class BedMaterialContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedMaterial" ):
                listener.enterBedMaterial(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedMaterial" ):
                listener.exitBedMaterial(self)


    class BedInternalCylinderModeContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedInternalCylinderMode" ):
                listener.enterBedInternalCylinderMode(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedInternalCylinderMode" ):
                listener.exitBedInternalCylinderMode(self)


    class BedClearanceContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedClearance" ):
                listener.enterBedClearance(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedClearance" ):
                listener.exitBedClearance(self)


    class BedDiameterContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedDiameter" ):
                listener.enterBedDiameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedDiameter" ):
                listener.exitBedDiameter(self)


    class BedRoughnessContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedRoughness" ):
                listener.enterBedRoughness(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedRoughness" ):
                listener.exitBedRoughness(self)


    class BedVisibilityBlockContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def visibilityProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.VisibilityPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.VisibilityPropertyContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedVisibilityBlock" ):
                listener.enterBedVisibilityBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedVisibilityBlock" ):
                listener.exitBedVisibilityBlock(self)


    class BedHeightContext(BedPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.BedPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBedHeight" ):
                listener.enterBedHeight(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBedHeight" ):
                listener.exitBedHeight(self)



    def bedProperty(self):

        localctx = BedParser.BedPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_bedProperty)
        self._la = 0 # Token type
        try:
            self.state = 136
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                localctx = BedParser.BedDiameterContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 94
                self.match(BedParser.T__3)
                self.state = 95
                self.match(BedParser.T__4)
                self.state = 96
                self.match(BedParser.NUMBER)
                self.state = 97
                self.match(BedParser.UNIT)
                self.state = 98
                self.match(BedParser.T__5)
                pass
            elif token in [7]:
                localctx = BedParser.BedHeightContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 99
                self.match(BedParser.T__6)
                self.state = 100
                self.match(BedParser.T__4)
                self.state = 101
                self.match(BedParser.NUMBER)
                self.state = 102
                self.match(BedParser.UNIT)
                self.state = 103
                self.match(BedParser.T__5)
                pass
            elif token in [8]:
                localctx = BedParser.BedWallThicknessContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 104
                self.match(BedParser.T__7)
                self.state = 105
                self.match(BedParser.T__4)
                self.state = 106
                self.match(BedParser.NUMBER)
                self.state = 107
                self.match(BedParser.UNIT)
                self.state = 108
                self.match(BedParser.T__5)
                pass
            elif token in [9]:
                localctx = BedParser.BedClearanceContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 109
                self.match(BedParser.T__8)
                self.state = 110
                self.match(BedParser.T__4)
                self.state = 111
                self.match(BedParser.NUMBER)
                self.state = 112
                self.match(BedParser.UNIT)
                self.state = 113
                self.match(BedParser.T__5)
                pass
            elif token in [10]:
                localctx = BedParser.BedMaterialContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 114
                self.match(BedParser.T__9)
                self.state = 115
                self.match(BedParser.T__4)
                self.state = 116
                self.match(BedParser.STRING)
                self.state = 117
                self.match(BedParser.T__5)
                pass
            elif token in [11]:
                localctx = BedParser.BedRoughnessContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 118
                self.match(BedParser.T__10)
                self.state = 119
                self.match(BedParser.T__4)
                self.state = 120
                self.match(BedParser.NUMBER)
                self.state = 121
                self.match(BedParser.UNIT)
                self.state = 122
                self.match(BedParser.T__5)
                pass
            elif token in [12]:
                localctx = BedParser.BedInternalCylinderModeContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 123
                self.match(BedParser.T__11)
                self.state = 124
                self.match(BedParser.T__4)
                self.state = 125
                self.match(BedParser.STRING)
                self.state = 126
                self.match(BedParser.T__5)
                pass
            elif token in [13]:
                localctx = BedParser.BedVisibilityBlockContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 127
                self.match(BedParser.T__12)
                self.state = 128
                self.match(BedParser.T__1)
                self.state = 130 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 129
                    self.visibilityProperty()
                    self.state = 132 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 507904) != 0)):
                        break

                self.state = 134
                self.match(BedParser.T__2)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VisibilityPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_visibilityProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class VisShowOuterContext(VisibilityPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.VisibilityPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVisShowOuter" ):
                listener.enterVisShowOuter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVisShowOuter" ):
                listener.exitVisShowOuter(self)


    class VisShowInternalContext(VisibilityPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.VisibilityPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVisShowInternal" ):
                listener.enterVisShowInternal(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVisShowInternal" ):
                listener.exitVisShowInternal(self)


    class VisShowParticlesContext(VisibilityPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.VisibilityPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVisShowParticles" ):
                listener.enterVisShowParticles(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVisShowParticles" ):
                listener.exitVisShowParticles(self)


    class VisShowBooleanToolsContext(VisibilityPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.VisibilityPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVisShowBooleanTools" ):
                listener.enterVisShowBooleanTools(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVisShowBooleanTools" ):
                listener.exitVisShowBooleanTools(self)


    class VisExportBooleanToolsContext(VisibilityPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.VisibilityPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVisExportBooleanTools" ):
                listener.enterVisExportBooleanTools(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVisExportBooleanTools" ):
                listener.exitVisExportBooleanTools(self)



    def visibilityProperty(self):

        localctx = BedParser.VisibilityPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_visibilityProperty)
        try:
            self.state = 158
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [14]:
                localctx = BedParser.VisShowOuterContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 138
                self.match(BedParser.T__13)
                self.state = 139
                self.match(BedParser.T__4)
                self.state = 140
                self.match(BedParser.BOOLEAN)
                self.state = 141
                self.match(BedParser.T__5)
                pass
            elif token in [15]:
                localctx = BedParser.VisShowInternalContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 142
                self.match(BedParser.T__14)
                self.state = 143
                self.match(BedParser.T__4)
                self.state = 144
                self.match(BedParser.BOOLEAN)
                self.state = 145
                self.match(BedParser.T__5)
                pass
            elif token in [16]:
                localctx = BedParser.VisShowParticlesContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 146
                self.match(BedParser.T__15)
                self.state = 147
                self.match(BedParser.T__4)
                self.state = 148
                self.match(BedParser.BOOLEAN)
                self.state = 149
                self.match(BedParser.T__5)
                pass
            elif token in [17]:
                localctx = BedParser.VisShowBooleanToolsContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 150
                self.match(BedParser.T__16)
                self.state = 151
                self.match(BedParser.T__4)
                self.state = 152
                self.match(BedParser.BOOLEAN)
                self.state = 153
                self.match(BedParser.T__5)
                pass
            elif token in [18]:
                localctx = BedParser.VisExportBooleanToolsContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 154
                self.match(BedParser.T__17)
                self.state = 155
                self.match(BedParser.T__4)
                self.state = 156
                self.match(BedParser.BOOLEAN)
                self.state = 157
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LidsSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lidsProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.LidsPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.LidsPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_lidsSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLidsSection" ):
                listener.enterLidsSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLidsSection" ):
                listener.exitLidsSection(self)




    def lidsSection(self):

        localctx = BedParser.LidsSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_lidsSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 160
            self.match(BedParser.T__18)
            self.state = 161
            self.match(BedParser.T__1)
            self.state = 163 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 162
                self.lidsProperty()
                self.state = 165 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 32505856) != 0)):
                    break

            self.state = 167
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LidsPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_lidsProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class LidsSealClearanceContext(LidsPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.LidsPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLidsSealClearance" ):
                listener.enterLidsSealClearance(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLidsSealClearance" ):
                listener.exitLidsSealClearance(self)


    class LidsTopTypeContext(LidsPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.LidsPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def lidType(self):
            return self.getTypedRuleContext(BedParser.LidTypeContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLidsTopType" ):
                listener.enterLidsTopType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLidsTopType" ):
                listener.exitLidsTopType(self)


    class LidsBottomTypeContext(LidsPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.LidsPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def lidType(self):
            return self.getTypedRuleContext(BedParser.LidTypeContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLidsBottomType" ):
                listener.enterLidsBottomType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLidsBottomType" ):
                listener.exitLidsBottomType(self)


    class LidsBottomThicknessContext(LidsPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.LidsPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLidsBottomThickness" ):
                listener.enterLidsBottomThickness(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLidsBottomThickness" ):
                listener.exitLidsBottomThickness(self)


    class LidsTopThicknessContext(LidsPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.LidsPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLidsTopThickness" ):
                listener.enterLidsTopThickness(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLidsTopThickness" ):
                listener.exitLidsTopThickness(self)



    def lidsProperty(self):

        localctx = BedParser.LidsPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_lidsProperty)
        try:
            self.state = 194
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [20]:
                localctx = BedParser.LidsTopTypeContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 169
                self.match(BedParser.T__19)
                self.state = 170
                self.match(BedParser.T__4)
                self.state = 171
                self.lidType()
                self.state = 172
                self.match(BedParser.T__5)
                pass
            elif token in [21]:
                localctx = BedParser.LidsBottomTypeContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 174
                self.match(BedParser.T__20)
                self.state = 175
                self.match(BedParser.T__4)
                self.state = 176
                self.lidType()
                self.state = 177
                self.match(BedParser.T__5)
                pass
            elif token in [22]:
                localctx = BedParser.LidsTopThicknessContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 179
                self.match(BedParser.T__21)
                self.state = 180
                self.match(BedParser.T__4)
                self.state = 181
                self.match(BedParser.NUMBER)
                self.state = 182
                self.match(BedParser.UNIT)
                self.state = 183
                self.match(BedParser.T__5)
                pass
            elif token in [23]:
                localctx = BedParser.LidsBottomThicknessContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 184
                self.match(BedParser.T__22)
                self.state = 185
                self.match(BedParser.T__4)
                self.state = 186
                self.match(BedParser.NUMBER)
                self.state = 187
                self.match(BedParser.UNIT)
                self.state = 188
                self.match(BedParser.T__5)
                pass
            elif token in [24]:
                localctx = BedParser.LidsSealClearanceContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 189
                self.match(BedParser.T__23)
                self.state = 190
                self.match(BedParser.T__4)
                self.state = 191
                self.match(BedParser.NUMBER)
                self.state = 192
                self.match(BedParser.UNIT)
                self.state = 193
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LidTypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_lidType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLidType" ):
                listener.enterLidType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLidType" ):
                listener.exitLidType(self)




    def lidType(self):

        localctx = BedParser.LidTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_lidType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 196
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 234881024) != 0) or _la==117):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParticlesSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def particlesProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.ParticlesPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.ParticlesPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_particlesSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesSection" ):
                listener.enterParticlesSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesSection" ):
                listener.exitParticlesSection(self)




    def particlesSection(self):

        localctx = BedParser.ParticlesSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_particlesSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 198
            self.match(BedParser.T__27)
            self.state = 199
            self.match(BedParser.T__1)
            self.state = 201 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 200
                self.particlesProperty()
                self.state = 203 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 1098974756880) != 0)):
                    break

            self.state = 205
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParticlesPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_particlesProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ParticlesSeedContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesSeed" ):
                listener.enterParticlesSeed(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesSeed" ):
                listener.exitParticlesSeed(self)


    class ParticlesCountContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesCount" ):
                listener.enterParticlesCount(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesCount" ):
                listener.exitParticlesCount(self)


    class ParticlesLinearDampingContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesLinearDamping" ):
                listener.enterParticlesLinearDamping(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesLinearDamping" ):
                listener.exitParticlesLinearDamping(self)


    class ParticlesDensityContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesDensity" ):
                listener.enterParticlesDensity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesDensity" ):
                listener.exitParticlesDensity(self)


    class ParticlesKindContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def particleKind(self):
            return self.getTypedRuleContext(BedParser.ParticleKindContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesKind" ):
                listener.enterParticlesKind(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesKind" ):
                listener.exitParticlesKind(self)


    class ParticlesDiameterContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesDiameter" ):
                listener.enterParticlesDiameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesDiameter" ):
                listener.exitParticlesDiameter(self)


    class ParticlesFrictionContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesFriction" ):
                listener.enterParticlesFriction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesFriction" ):
                listener.exitParticlesFriction(self)


    class ParticlesMassContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesMass" ):
                listener.enterParticlesMass(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesMass" ):
                listener.exitParticlesMass(self)


    class ParticlesTargetPorosityContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesTargetPorosity" ):
                listener.enterParticlesTargetPorosity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesTargetPorosity" ):
                listener.exitParticlesTargetPorosity(self)


    class ParticlesRollingFrictionContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesRollingFriction" ):
                listener.enterParticlesRollingFriction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesRollingFriction" ):
                listener.exitParticlesRollingFriction(self)


    class ParticlesAngularDampingContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesAngularDamping" ):
                listener.enterParticlesAngularDamping(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesAngularDamping" ):
                listener.exitParticlesAngularDamping(self)


    class ParticlesRestitutionContext(ParticlesPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ParticlesPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticlesRestitution" ):
                listener.enterParticlesRestitution(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticlesRestitution" ):
                listener.exitParticlesRestitution(self)



    def particlesProperty(self):

        localctx = BedParser.ParticlesPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_particlesProperty)
        try:
            self.state = 259
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [29]:
                localctx = BedParser.ParticlesKindContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 207
                self.match(BedParser.T__28)
                self.state = 208
                self.match(BedParser.T__4)
                self.state = 209
                self.particleKind()
                self.state = 210
                self.match(BedParser.T__5)
                pass
            elif token in [4]:
                localctx = BedParser.ParticlesDiameterContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 212
                self.match(BedParser.T__3)
                self.state = 213
                self.match(BedParser.T__4)
                self.state = 214
                self.match(BedParser.NUMBER)
                self.state = 215
                self.match(BedParser.UNIT)
                self.state = 216
                self.match(BedParser.T__5)
                pass
            elif token in [30]:
                localctx = BedParser.ParticlesCountContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 217
                self.match(BedParser.T__29)
                self.state = 218
                self.match(BedParser.T__4)
                self.state = 219
                self.match(BedParser.NUMBER)
                self.state = 220
                self.match(BedParser.T__5)
                pass
            elif token in [31]:
                localctx = BedParser.ParticlesTargetPorosityContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 221
                self.match(BedParser.T__30)
                self.state = 222
                self.match(BedParser.T__4)
                self.state = 223
                self.match(BedParser.NUMBER)
                self.state = 224
                self.match(BedParser.T__5)
                pass
            elif token in [32]:
                localctx = BedParser.ParticlesDensityContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 225
                self.match(BedParser.T__31)
                self.state = 226
                self.match(BedParser.T__4)
                self.state = 227
                self.match(BedParser.NUMBER)
                self.state = 228
                self.match(BedParser.UNIT)
                self.state = 229
                self.match(BedParser.T__5)
                pass
            elif token in [33]:
                localctx = BedParser.ParticlesMassContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 230
                self.match(BedParser.T__32)
                self.state = 231
                self.match(BedParser.T__4)
                self.state = 232
                self.match(BedParser.NUMBER)
                self.state = 233
                self.match(BedParser.UNIT)
                self.state = 234
                self.match(BedParser.T__5)
                pass
            elif token in [34]:
                localctx = BedParser.ParticlesRestitutionContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 235
                self.match(BedParser.T__33)
                self.state = 236
                self.match(BedParser.T__4)
                self.state = 237
                self.match(BedParser.NUMBER)
                self.state = 238
                self.match(BedParser.T__5)
                pass
            elif token in [35]:
                localctx = BedParser.ParticlesFrictionContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 239
                self.match(BedParser.T__34)
                self.state = 240
                self.match(BedParser.T__4)
                self.state = 241
                self.match(BedParser.NUMBER)
                self.state = 242
                self.match(BedParser.T__5)
                pass
            elif token in [36]:
                localctx = BedParser.ParticlesRollingFrictionContext(self, localctx)
                self.enterOuterAlt(localctx, 9)
                self.state = 243
                self.match(BedParser.T__35)
                self.state = 244
                self.match(BedParser.T__4)
                self.state = 245
                self.match(BedParser.NUMBER)
                self.state = 246
                self.match(BedParser.T__5)
                pass
            elif token in [37]:
                localctx = BedParser.ParticlesLinearDampingContext(self, localctx)
                self.enterOuterAlt(localctx, 10)
                self.state = 247
                self.match(BedParser.T__36)
                self.state = 248
                self.match(BedParser.T__4)
                self.state = 249
                self.match(BedParser.NUMBER)
                self.state = 250
                self.match(BedParser.T__5)
                pass
            elif token in [38]:
                localctx = BedParser.ParticlesAngularDampingContext(self, localctx)
                self.enterOuterAlt(localctx, 11)
                self.state = 251
                self.match(BedParser.T__37)
                self.state = 252
                self.match(BedParser.T__4)
                self.state = 253
                self.match(BedParser.NUMBER)
                self.state = 254
                self.match(BedParser.T__5)
                pass
            elif token in [39]:
                localctx = BedParser.ParticlesSeedContext(self, localctx)
                self.enterOuterAlt(localctx, 12)
                self.state = 255
                self.match(BedParser.T__38)
                self.state = 256
                self.match(BedParser.T__4)
                self.state = 257
                self.match(BedParser.NUMBER)
                self.state = 258
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParticleKindContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_particleKind

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParticleKind" ):
                listener.enterParticleKind(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParticleKind" ):
                listener.exitParticleKind(self)




    def particleKind(self):

        localctx = BedParser.ParticleKindContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_particleKind)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 261
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 7696581394432) != 0) or _la==117):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PackingSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def packingProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.PackingPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.PackingPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_packingSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingSection" ):
                listener.enterPackingSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingSection" ):
                listener.exitPackingSection(self)




    def packingSection(self):

        localctx = BedParser.PackingSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_packingSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 263
            self.match(BedParser.T__42)
            self.state = 264
            self.match(BedParser.T__1)
            self.state = 266 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 265
                self.packingProperty()
                self.state = 268 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 4611668426241343488) != 0)):
                    break

            self.state = 270
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PackingPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_packingProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class PackingDampingContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingDamping" ):
                listener.enterPackingDamping(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingDamping" ):
                listener.exitPackingDamping(self)


    class PackingSphereLonContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingSphereLon" ):
                listener.enterPackingSphereLon(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingSphereLon" ):
                listener.exitPackingSphereLon(self)


    class PackingCollisionMarginContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingCollisionMargin" ):
                listener.enterPackingCollisionMargin(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingCollisionMargin" ):
                listener.exitPackingCollisionMargin(self)


    class PackingGapContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingGap" ):
                listener.enterPackingGap(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingGap" ):
                listener.exitPackingGap(self)


    class PackingSubstepsContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingSubsteps" ):
                listener.enterPackingSubsteps(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingSubsteps" ):
                listener.exitPackingSubsteps(self)


    class PackingMaxTimeContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingMaxTime" ):
                listener.enterPackingMaxTime(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingMaxTime" ):
                listener.exitPackingMaxTime(self)


    class PackingGravityContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingGravity" ):
                listener.enterPackingGravity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingGravity" ):
                listener.exitPackingGravity(self)


    class PackingRandomSeedContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingRandomSeed" ):
                listener.enterPackingRandomSeed(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingRandomSeed" ):
                listener.exitPackingRandomSeed(self)


    class PackingMaxAttemptsContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingMaxAttempts" ):
                listener.enterPackingMaxAttempts(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingMaxAttempts" ):
                listener.exitPackingMaxAttempts(self)


    class PackingStrictValidationContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingStrictValidation" ):
                listener.enterPackingStrictValidation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingStrictValidation" ):
                listener.exitPackingStrictValidation(self)


    class PackingUseLegacyDropContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingUseLegacyDrop" ):
                listener.enterPackingUseLegacyDrop(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingUseLegacyDrop" ):
                listener.exitPackingUseLegacyDrop(self)


    class PackingRestVelocityContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingRestVelocity" ):
                listener.enterPackingRestVelocity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingRestVelocity" ):
                listener.exitPackingRestVelocity(self)


    class PackingStepXContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingStepX" ):
                listener.enterPackingStepX(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingStepX" ):
                listener.exitPackingStepX(self)


    class PackingDemBlockContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def demProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.DemPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.DemPropertyContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingDemBlock" ):
                listener.enterPackingDemBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingDemBlock" ):
                listener.exitPackingDemBlock(self)


    class PackingIterationsContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingIterations" ):
                listener.enterPackingIterations(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingIterations" ):
                listener.exitPackingIterations(self)


    class PackingSphereLatContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingSphereLat" ):
                listener.enterPackingSphereLat(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingSphereLat" ):
                listener.exitPackingSphereLat(self)


    class PackingMeshSegmentosContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingMeshSegmentos" ):
                listener.enterPackingMeshSegmentos(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingMeshSegmentos" ):
                listener.exitPackingMeshSegmentos(self)


    class PackingMethodPropContext(PackingPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.PackingPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def packingMethod(self):
            return self.getTypedRuleContext(BedParser.PackingMethodContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingMethodProp" ):
                listener.enterPackingMethodProp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingMethodProp" ):
                listener.exitPackingMethodProp(self)



    def packingProperty(self):

        localctx = BedParser.PackingPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_packingProperty)
        self._la = 0 # Token type
        try:
            self.state = 356
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [44]:
                localctx = BedParser.PackingMethodPropContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 272
                self.match(BedParser.T__43)
                self.state = 273
                self.match(BedParser.T__4)
                self.state = 274
                self.packingMethod()
                self.state = 275
                self.match(BedParser.T__5)
                pass
            elif token in [45]:
                localctx = BedParser.PackingGravityContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 277
                self.match(BedParser.T__44)
                self.state = 278
                self.match(BedParser.T__4)
                self.state = 279
                self.match(BedParser.NUMBER)
                self.state = 280
                self.match(BedParser.UNIT)
                self.state = 281
                self.match(BedParser.T__5)
                pass
            elif token in [46]:
                localctx = BedParser.PackingSubstepsContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 282
                self.match(BedParser.T__45)
                self.state = 283
                self.match(BedParser.T__4)
                self.state = 284
                self.match(BedParser.NUMBER)
                self.state = 285
                self.match(BedParser.T__5)
                pass
            elif token in [47]:
                localctx = BedParser.PackingIterationsContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 286
                self.match(BedParser.T__46)
                self.state = 287
                self.match(BedParser.T__4)
                self.state = 288
                self.match(BedParser.NUMBER)
                self.state = 289
                self.match(BedParser.T__5)
                pass
            elif token in [48]:
                localctx = BedParser.PackingDampingContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 290
                self.match(BedParser.T__47)
                self.state = 291
                self.match(BedParser.T__4)
                self.state = 292
                self.match(BedParser.NUMBER)
                self.state = 293
                self.match(BedParser.T__5)
                pass
            elif token in [49]:
                localctx = BedParser.PackingRestVelocityContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 294
                self.match(BedParser.T__48)
                self.state = 295
                self.match(BedParser.T__4)
                self.state = 296
                self.match(BedParser.NUMBER)
                self.state = 297
                self.match(BedParser.UNIT)
                self.state = 298
                self.match(BedParser.T__5)
                pass
            elif token in [50]:
                localctx = BedParser.PackingMaxTimeContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 299
                self.match(BedParser.T__49)
                self.state = 300
                self.match(BedParser.T__4)
                self.state = 301
                self.match(BedParser.NUMBER)
                self.state = 302
                self.match(BedParser.UNIT)
                self.state = 303
                self.match(BedParser.T__5)
                pass
            elif token in [51]:
                localctx = BedParser.PackingCollisionMarginContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 304
                self.match(BedParser.T__50)
                self.state = 305
                self.match(BedParser.T__4)
                self.state = 306
                self.match(BedParser.NUMBER)
                self.state = 307
                self.match(BedParser.UNIT)
                self.state = 308
                self.match(BedParser.T__5)
                pass
            elif token in [52]:
                localctx = BedParser.PackingGapContext(self, localctx)
                self.enterOuterAlt(localctx, 9)
                self.state = 309
                self.match(BedParser.T__51)
                self.state = 310
                self.match(BedParser.T__4)
                self.state = 311
                self.match(BedParser.NUMBER)
                self.state = 312
                self.match(BedParser.UNIT)
                self.state = 313
                self.match(BedParser.T__5)
                pass
            elif token in [53]:
                localctx = BedParser.PackingRandomSeedContext(self, localctx)
                self.enterOuterAlt(localctx, 10)
                self.state = 314
                self.match(BedParser.T__52)
                self.state = 315
                self.match(BedParser.T__4)
                self.state = 316
                self.match(BedParser.NUMBER)
                self.state = 317
                self.match(BedParser.T__5)
                pass
            elif token in [54]:
                localctx = BedParser.PackingMaxAttemptsContext(self, localctx)
                self.enterOuterAlt(localctx, 11)
                self.state = 318
                self.match(BedParser.T__53)
                self.state = 319
                self.match(BedParser.T__4)
                self.state = 320
                self.match(BedParser.NUMBER)
                self.state = 321
                self.match(BedParser.T__5)
                pass
            elif token in [55]:
                localctx = BedParser.PackingStrictValidationContext(self, localctx)
                self.enterOuterAlt(localctx, 12)
                self.state = 322
                self.match(BedParser.T__54)
                self.state = 323
                self.match(BedParser.T__4)
                self.state = 324
                self.match(BedParser.BOOLEAN)
                self.state = 325
                self.match(BedParser.T__5)
                pass
            elif token in [56]:
                localctx = BedParser.PackingStepXContext(self, localctx)
                self.enterOuterAlt(localctx, 13)
                self.state = 326
                self.match(BedParser.T__55)
                self.state = 327
                self.match(BedParser.T__4)
                self.state = 328
                self.match(BedParser.NUMBER)
                self.state = 329
                self.match(BedParser.UNIT)
                self.state = 330
                self.match(BedParser.T__5)
                pass
            elif token in [57]:
                localctx = BedParser.PackingMeshSegmentosContext(self, localctx)
                self.enterOuterAlt(localctx, 14)
                self.state = 331
                self.match(BedParser.T__56)
                self.state = 332
                self.match(BedParser.T__4)
                self.state = 333
                self.match(BedParser.NUMBER)
                self.state = 334
                self.match(BedParser.T__5)
                pass
            elif token in [58]:
                localctx = BedParser.PackingSphereLatContext(self, localctx)
                self.enterOuterAlt(localctx, 15)
                self.state = 335
                self.match(BedParser.T__57)
                self.state = 336
                self.match(BedParser.T__4)
                self.state = 337
                self.match(BedParser.NUMBER)
                self.state = 338
                self.match(BedParser.T__5)
                pass
            elif token in [59]:
                localctx = BedParser.PackingSphereLonContext(self, localctx)
                self.enterOuterAlt(localctx, 16)
                self.state = 339
                self.match(BedParser.T__58)
                self.state = 340
                self.match(BedParser.T__4)
                self.state = 341
                self.match(BedParser.NUMBER)
                self.state = 342
                self.match(BedParser.T__5)
                pass
            elif token in [60]:
                localctx = BedParser.PackingUseLegacyDropContext(self, localctx)
                self.enterOuterAlt(localctx, 17)
                self.state = 343
                self.match(BedParser.T__59)
                self.state = 344
                self.match(BedParser.T__4)
                self.state = 345
                self.match(BedParser.BOOLEAN)
                self.state = 346
                self.match(BedParser.T__5)
                pass
            elif token in [61]:
                localctx = BedParser.PackingDemBlockContext(self, localctx)
                self.enterOuterAlt(localctx, 18)
                self.state = 347
                self.match(BedParser.T__60)
                self.state = 348
                self.match(BedParser.T__1)
                self.state = 350 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 349
                    self.demProperty()
                    self.state = 352 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (((((_la - 34)) & ~0x3f) == 0 and ((1 << (_la - 34)) & 8321517603) != 0)):
                        break

                self.state = 354
                self.match(BedParser.T__2)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DemPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_demProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class DemSeedContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemSeed" ):
                listener.enterDemSeed(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemSeed" ):
                listener.exitDemSeed(self)


    class DemGravityContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemGravity" ):
                listener.enterDemGravity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemGravity" ):
                listener.exitDemGravity(self)


    class DemSettleThresholdContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemSettleThreshold" ):
                listener.enterDemSettleThreshold(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemSettleThreshold" ):
                listener.exitDemSettleThreshold(self)


    class DemDampingContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemDamping" ):
                listener.enterDemDamping(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemDamping" ):
                listener.exitDemDamping(self)


    class DemFrictionContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemFriction" ):
                listener.enterDemFriction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemFriction" ):
                listener.exitDemFriction(self)


    class DemStepsContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemSteps" ):
                listener.enterDemSteps(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemSteps" ):
                listener.exitDemSteps(self)


    class DemStiffnessContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemStiffness" ):
                listener.enterDemStiffness(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemStiffness" ):
                listener.exitDemStiffness(self)


    class DemRestitutionContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemRestitution" ):
                listener.enterDemRestitution(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemRestitution" ):
                listener.exitDemRestitution(self)


    class DemTimeStepContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemTimeStep" ):
                listener.enterDemTimeStep(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemTimeStep" ):
                listener.exitDemTimeStep(self)


    class DemMaxVelocityContext(DemPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.DemPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDemMaxVelocity" ):
                listener.enterDemMaxVelocity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDemMaxVelocity" ):
                listener.exitDemMaxVelocity(self)



    def demProperty(self):

        localctx = BedParser.DemPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_demProperty)
        try:
            self.state = 402
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [62]:
                localctx = BedParser.DemTimeStepContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 358
                self.match(BedParser.T__61)
                self.state = 359
                self.match(BedParser.T__4)
                self.state = 360
                self.match(BedParser.NUMBER)
                self.state = 361
                self.match(BedParser.UNIT)
                self.state = 362
                self.match(BedParser.T__5)
                pass
            elif token in [63]:
                localctx = BedParser.DemStepsContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 363
                self.match(BedParser.T__62)
                self.state = 364
                self.match(BedParser.T__4)
                self.state = 365
                self.match(BedParser.NUMBER)
                self.state = 366
                self.match(BedParser.T__5)
                pass
            elif token in [45]:
                localctx = BedParser.DemGravityContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 367
                self.match(BedParser.T__44)
                self.state = 368
                self.match(BedParser.T__4)
                self.state = 369
                self.match(BedParser.NUMBER)
                self.state = 370
                self.match(BedParser.UNIT)
                self.state = 371
                self.match(BedParser.T__5)
                pass
            elif token in [64]:
                localctx = BedParser.DemStiffnessContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 372
                self.match(BedParser.T__63)
                self.state = 373
                self.match(BedParser.T__4)
                self.state = 374
                self.match(BedParser.NUMBER)
                self.state = 375
                self.match(BedParser.T__5)
                pass
            elif token in [48]:
                localctx = BedParser.DemDampingContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 376
                self.match(BedParser.T__47)
                self.state = 377
                self.match(BedParser.T__4)
                self.state = 378
                self.match(BedParser.NUMBER)
                self.state = 379
                self.match(BedParser.T__5)
                pass
            elif token in [35]:
                localctx = BedParser.DemFrictionContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 380
                self.match(BedParser.T__34)
                self.state = 381
                self.match(BedParser.T__4)
                self.state = 382
                self.match(BedParser.NUMBER)
                self.state = 383
                self.match(BedParser.T__5)
                pass
            elif token in [34]:
                localctx = BedParser.DemRestitutionContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 384
                self.match(BedParser.T__33)
                self.state = 385
                self.match(BedParser.T__4)
                self.state = 386
                self.match(BedParser.NUMBER)
                self.state = 387
                self.match(BedParser.T__5)
                pass
            elif token in [65]:
                localctx = BedParser.DemSettleThresholdContext(self, localctx)
                self.enterOuterAlt(localctx, 8)
                self.state = 388
                self.match(BedParser.T__64)
                self.state = 389
                self.match(BedParser.T__4)
                self.state = 390
                self.match(BedParser.NUMBER)
                self.state = 391
                self.match(BedParser.UNIT)
                self.state = 392
                self.match(BedParser.T__5)
                pass
            elif token in [66]:
                localctx = BedParser.DemMaxVelocityContext(self, localctx)
                self.enterOuterAlt(localctx, 9)
                self.state = 393
                self.match(BedParser.T__65)
                self.state = 394
                self.match(BedParser.T__4)
                self.state = 395
                self.match(BedParser.NUMBER)
                self.state = 396
                self.match(BedParser.UNIT)
                self.state = 397
                self.match(BedParser.T__5)
                pass
            elif token in [39]:
                localctx = BedParser.DemSeedContext(self, localctx)
                self.enterOuterAlt(localctx, 10)
                self.state = 398
                self.match(BedParser.T__38)
                self.state = 399
                self.match(BedParser.T__4)
                self.state = 400
                self.match(BedParser.NUMBER)
                self.state = 401
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PackingMethodContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_packingMethod

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPackingMethod" ):
                listener.enterPackingMethod(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPackingMethod" ):
                listener.exitPackingMethod(self)




    def packingMethod(self):

        localctx = BedParser.PackingMethodContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_packingMethod)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 404
            _la = self._input.LA(1)
            if not(_la==67 or _la==117):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExportSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def exportProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.ExportPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.ExportPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_exportSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportSection" ):
                listener.enterExportSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportSection" ):
                listener.exitExportSection(self)




    def exportSection(self):

        localctx = BedParser.ExportSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_exportSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 406
            self.match(BedParser.T__67)
            self.state = 407
            self.match(BedParser.T__1)
            self.state = 409 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 408
                self.exportProperty()
                self.state = 411 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (((((_la - 69)) & ~0x3f) == 0 and ((1 << (_la - 69)) & 505) != 0)):
                    break

            self.state = 413
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExportPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_exportProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ExportScaleContext(ExportPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ExportPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportScale" ):
                listener.enterExportScale(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportScale" ):
                listener.exitExportScale(self)


    class ExportMergeDistanceContext(ExportPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ExportPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportMergeDistance" ):
                listener.enterExportMergeDistance(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportMergeDistance" ):
                listener.exitExportMergeDistance(self)


    class ExportWallModeContext(ExportPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ExportPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def wallMode(self):
            return self.getTypedRuleContext(BedParser.WallModeContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportWallMode" ):
                listener.enterExportWallMode(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportWallMode" ):
                listener.exitExportWallMode(self)


    class ExportFluidModeContext(ExportPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ExportPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def fluidMode(self):
            return self.getTypedRuleContext(BedParser.FluidModeContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportFluidMode" ):
                listener.enterExportFluidMode(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportFluidMode" ):
                listener.exitExportFluidMode(self)


    class ExportManifoldCheckContext(ExportPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ExportPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportManifoldCheck" ):
                listener.enterExportManifoldCheck(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportManifoldCheck" ):
                listener.exitExportManifoldCheck(self)


    class ExportFormatsContext(ExportPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ExportPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def formatList(self):
            return self.getTypedRuleContext(BedParser.FormatListContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportFormats" ):
                listener.enterExportFormats(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportFormats" ):
                listener.exitExportFormats(self)


    class ExportUnitsContext(ExportPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.ExportPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExportUnits" ):
                listener.enterExportUnits(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExportUnits" ):
                listener.exitExportUnits(self)



    def exportProperty(self):

        localctx = BedParser.ExportPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_exportProperty)
        try:
            self.state = 449
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [69]:
                localctx = BedParser.ExportFormatsContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 415
                self.match(BedParser.T__68)
                self.state = 416
                self.match(BedParser.T__4)
                self.state = 417
                self.match(BedParser.T__69)
                self.state = 418
                self.formatList()
                self.state = 419
                self.match(BedParser.T__70)
                self.state = 420
                self.match(BedParser.T__5)
                pass
            elif token in [72]:
                localctx = BedParser.ExportUnitsContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 422
                self.match(BedParser.T__71)
                self.state = 423
                self.match(BedParser.T__4)
                self.state = 424
                self.match(BedParser.STRING)
                self.state = 425
                self.match(BedParser.T__5)
                pass
            elif token in [73]:
                localctx = BedParser.ExportScaleContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 426
                self.match(BedParser.T__72)
                self.state = 427
                self.match(BedParser.T__4)
                self.state = 428
                self.match(BedParser.NUMBER)
                self.state = 429
                self.match(BedParser.T__5)
                pass
            elif token in [74]:
                localctx = BedParser.ExportWallModeContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 430
                self.match(BedParser.T__73)
                self.state = 431
                self.match(BedParser.T__4)
                self.state = 432
                self.wallMode()
                self.state = 433
                self.match(BedParser.T__5)
                pass
            elif token in [75]:
                localctx = BedParser.ExportFluidModeContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 435
                self.match(BedParser.T__74)
                self.state = 436
                self.match(BedParser.T__4)
                self.state = 437
                self.fluidMode()
                self.state = 438
                self.match(BedParser.T__5)
                pass
            elif token in [76]:
                localctx = BedParser.ExportManifoldCheckContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 440
                self.match(BedParser.T__75)
                self.state = 441
                self.match(BedParser.T__4)
                self.state = 442
                self.match(BedParser.BOOLEAN)
                self.state = 443
                self.match(BedParser.T__5)
                pass
            elif token in [77]:
                localctx = BedParser.ExportMergeDistanceContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 444
                self.match(BedParser.T__76)
                self.state = 445
                self.match(BedParser.T__4)
                self.state = 446
                self.match(BedParser.NUMBER)
                self.state = 447
                self.match(BedParser.UNIT)
                self.state = 448
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FormatListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(BedParser.STRING)
            else:
                return self.getToken(BedParser.STRING, i)

        def getRuleIndex(self):
            return BedParser.RULE_formatList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFormatList" ):
                listener.enterFormatList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFormatList" ):
                listener.exitFormatList(self)




    def formatList(self):

        localctx = BedParser.FormatListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_formatList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 451
            self.match(BedParser.STRING)
            self.state = 456
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==78:
                self.state = 452
                self.match(BedParser.T__77)
                self.state = 453
                self.match(BedParser.STRING)
                self.state = 458
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WallModeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_wallMode

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWallMode" ):
                listener.enterWallMode(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWallMode" ):
                listener.exitWallMode(self)




    def wallMode(self):

        localctx = BedParser.WallModeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_wallMode)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 459
            _la = self._input.LA(1)
            if not(((((_la - 79)) & ~0x3f) == 0 and ((1 << (_la - 79)) & 274877906947) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FluidModeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_fluidMode

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFluidMode" ):
                listener.enterFluidMode(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFluidMode" ):
                listener.exitFluidMode(self)




    def fluidMode(self):

        localctx = BedParser.FluidModeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_fluidMode)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 461
            _la = self._input.LA(1)
            if not(_la==27 or _la==81 or _la==117):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CfdSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def cfdProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.CfdPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.CfdPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_cfdSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdSection" ):
                listener.enterCfdSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdSection" ):
                listener.exitCfdSection(self)




    def cfdSection(self):

        localctx = BedParser.CfdSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_cfdSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 463
            self.match(BedParser.T__81)
            self.state = 464
            self.match(BedParser.T__1)
            self.state = 466 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 465
                self.cfdProperty()
                self.state = 468 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (((((_la - 83)) & ~0x3f) == 0 and ((1 << (_la - 83)) & 127) != 0)):
                    break

            self.state = 470
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CfdPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_cfdProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class CfdInletVelocityContext(CfdPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.CfdPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdInletVelocity" ):
                listener.enterCfdInletVelocity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdInletVelocity" ):
                listener.exitCfdInletVelocity(self)


    class CfdWriteFieldsContext(CfdPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.CfdPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdWriteFields" ):
                listener.enterCfdWriteFields(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdWriteFields" ):
                listener.exitCfdWriteFields(self)


    class CfdMaxIterationsContext(CfdPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.CfdPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdMaxIterations" ):
                listener.enterCfdMaxIterations(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdMaxIterations" ):
                listener.exitCfdMaxIterations(self)


    class CfdConvergenceCriteriaContext(CfdPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.CfdPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdConvergenceCriteria" ):
                listener.enterCfdConvergenceCriteria(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdConvergenceCriteria" ):
                listener.exitCfdConvergenceCriteria(self)


    class CfdFluidViscosityContext(CfdPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.CfdPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdFluidViscosity" ):
                listener.enterCfdFluidViscosity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdFluidViscosity" ):
                listener.exitCfdFluidViscosity(self)


    class CfdRegimePropContext(CfdPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.CfdPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def cfdRegime(self):
            return self.getTypedRuleContext(BedParser.CfdRegimeContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdRegimeProp" ):
                listener.enterCfdRegimeProp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdRegimeProp" ):
                listener.exitCfdRegimeProp(self)


    class CfdFluidDensityContext(CfdPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.CfdPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdFluidDensity" ):
                listener.enterCfdFluidDensity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdFluidDensity" ):
                listener.exitCfdFluidDensity(self)



    def cfdProperty(self):

        localctx = BedParser.CfdPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_cfdProperty)
        try:
            self.state = 504
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [83]:
                localctx = BedParser.CfdRegimePropContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 472
                self.match(BedParser.T__82)
                self.state = 473
                self.match(BedParser.T__4)
                self.state = 474
                self.cfdRegime()
                self.state = 475
                self.match(BedParser.T__5)
                pass
            elif token in [84]:
                localctx = BedParser.CfdInletVelocityContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 477
                self.match(BedParser.T__83)
                self.state = 478
                self.match(BedParser.T__4)
                self.state = 479
                self.match(BedParser.NUMBER)
                self.state = 480
                self.match(BedParser.UNIT)
                self.state = 481
                self.match(BedParser.T__5)
                pass
            elif token in [85]:
                localctx = BedParser.CfdFluidDensityContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 482
                self.match(BedParser.T__84)
                self.state = 483
                self.match(BedParser.T__4)
                self.state = 484
                self.match(BedParser.NUMBER)
                self.state = 485
                self.match(BedParser.UNIT)
                self.state = 486
                self.match(BedParser.T__5)
                pass
            elif token in [86]:
                localctx = BedParser.CfdFluidViscosityContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 487
                self.match(BedParser.T__85)
                self.state = 488
                self.match(BedParser.T__4)
                self.state = 489
                self.match(BedParser.NUMBER)
                self.state = 490
                self.match(BedParser.UNIT)
                self.state = 491
                self.match(BedParser.T__5)
                pass
            elif token in [87]:
                localctx = BedParser.CfdMaxIterationsContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 492
                self.match(BedParser.T__86)
                self.state = 493
                self.match(BedParser.T__4)
                self.state = 494
                self.match(BedParser.NUMBER)
                self.state = 495
                self.match(BedParser.T__5)
                pass
            elif token in [88]:
                localctx = BedParser.CfdConvergenceCriteriaContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 496
                self.match(BedParser.T__87)
                self.state = 497
                self.match(BedParser.T__4)
                self.state = 498
                self.match(BedParser.NUMBER)
                self.state = 499
                self.match(BedParser.T__5)
                pass
            elif token in [89]:
                localctx = BedParser.CfdWriteFieldsContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 500
                self.match(BedParser.T__88)
                self.state = 501
                self.match(BedParser.T__4)
                self.state = 502
                self.match(BedParser.BOOLEAN)
                self.state = 503
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CfdRegimeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_cfdRegime

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCfdRegime" ):
                listener.enterCfdRegime(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCfdRegime" ):
                listener.exitCfdRegime(self)




    def cfdRegime(self):

        localctx = BedParser.CfdRegimeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_cfdRegime)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 506
            _la = self._input.LA(1)
            if not(((((_la - 90)) & ~0x3f) == 0 and ((1 << (_la - 90)) & 134217731) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GeometrySectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def geometryProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.GeometryPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.GeometryPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_geometrySection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGeometrySection" ):
                listener.enterGeometrySection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGeometrySection" ):
                listener.exitGeometrySection(self)




    def geometrySection(self):

        localctx = BedParser.GeometrySectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_geometrySection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 508
            self.match(BedParser.T__91)
            self.state = 509
            self.match(BedParser.T__1)
            self.state = 511 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 510
                self.geometryProperty()
                self.state = 513 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==93):
                    break

            self.state = 515
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GeometryPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_geometryProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class GeometryModePropContext(GeometryPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.GeometryPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def geometryMode(self):
            return self.getTypedRuleContext(BedParser.GeometryModeContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGeometryModeProp" ):
                listener.enterGeometryModeProp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGeometryModeProp" ):
                listener.exitGeometryModeProp(self)



    def geometryProperty(self):

        localctx = BedParser.GeometryPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_geometryProperty)
        try:
            localctx = BedParser.GeometryModePropContext(self, localctx)
            self.enterOuterAlt(localctx, 1)
            self.state = 517
            self.match(BedParser.T__92)
            self.state = 518
            self.match(BedParser.T__4)
            self.state = 519
            self.geometryMode()
            self.state = 520
            self.match(BedParser.T__5)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GeometryModeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_geometryMode

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGeometryMode" ):
                listener.enterGeometryMode(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGeometryMode" ):
                listener.exitGeometryMode(self)




    def geometryMode(self):

        localctx = BedParser.GeometryModeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_geometryMode)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 522
            _la = self._input.LA(1)
            if not(((((_la - 94)) & ~0x3f) == 0 and ((1 << (_la - 94)) & 8388615) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenerationSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def generationProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.GenerationPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.GenerationPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_generationSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGenerationSection" ):
                listener.enterGenerationSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGenerationSection" ):
                listener.exitGenerationSection(self)




    def generationSection(self):

        localctx = BedParser.GenerationSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_generationSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 524
            self.match(BedParser.T__96)
            self.state = 525
            self.match(BedParser.T__1)
            self.state = 527 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 526
                self.generationProperty()
                self.state = 529 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==98):
                    break

            self.state = 531
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenerationPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_generationProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class GenerationBackendPropContext(GenerationPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.GenerationPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def generationBackend(self):
            return self.getTypedRuleContext(BedParser.GenerationBackendContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGenerationBackendProp" ):
                listener.enterGenerationBackendProp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGenerationBackendProp" ):
                listener.exitGenerationBackendProp(self)



    def generationProperty(self):

        localctx = BedParser.GenerationPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_generationProperty)
        try:
            localctx = BedParser.GenerationBackendPropContext(self, localctx)
            self.enterOuterAlt(localctx, 1)
            self.state = 533
            self.match(BedParser.T__97)
            self.state = 534
            self.match(BedParser.T__4)
            self.state = 535
            self.generationBackend()
            self.state = 536
            self.match(BedParser.T__5)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GenerationBackendContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def getRuleIndex(self):
            return BedParser.RULE_generationBackend

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGenerationBackend" ):
                listener.enterGenerationBackend(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGenerationBackend" ):
                listener.exitGenerationBackend(self)




    def generationBackend(self):

        localctx = BedParser.GenerationBackendContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_generationBackend)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 538
            _la = self._input.LA(1)
            if not(((((_la - 99)) & ~0x3f) == 0 and ((1 << (_la - 99)) & 262147) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SliceSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def sliceProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.SlicePropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.SlicePropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_sliceSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSliceSection" ):
                listener.enterSliceSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSliceSection" ):
                listener.exitSliceSection(self)




    def sliceSection(self):

        localctx = BedParser.SliceSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_sliceSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 540
            self.match(BedParser.T__100)
            self.state = 541
            self.match(BedParser.T__1)
            self.state = 543 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 542
                self.sliceProperty()
                self.state = 545 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (((((_la - 102)) & ~0x3f) == 0 and ((1 << (_la - 102)) & 63) != 0)):
                    break

            self.state = 547
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SlicePropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_sliceProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class SliceThicknessContext(SlicePropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.SlicePropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSliceThickness" ):
                listener.enterSliceThickness(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSliceThickness" ):
                listener.exitSliceThickness(self)


    class SlicePreservePackingContext(SlicePropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.SlicePropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSlicePreservePacking" ):
                listener.enterSlicePreservePacking(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSlicePreservePacking" ):
                listener.exitSlicePreservePacking(self)


    class SliceEnabledContext(SlicePropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.SlicePropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSliceEnabled" ):
                listener.enterSliceEnabled(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSliceEnabled" ):
                listener.exitSliceEnabled(self)


    class SlicePositionContext(SlicePropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.SlicePropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSlicePosition" ):
                listener.enterSlicePosition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSlicePosition" ):
                listener.exitSlicePosition(self)


    class SliceAxisContext(SlicePropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.SlicePropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(BedParser.STRING, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSliceAxis" ):
                listener.enterSliceAxis(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSliceAxis" ):
                listener.exitSliceAxis(self)


    class SliceKeepOnlyContext(SlicePropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.SlicePropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def BOOLEAN(self):
            return self.getToken(BedParser.BOOLEAN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSliceKeepOnly" ):
                listener.enterSliceKeepOnly(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSliceKeepOnly" ):
                listener.exitSliceKeepOnly(self)



    def sliceProperty(self):

        localctx = BedParser.SlicePropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_sliceProperty)
        try:
            self.state = 575
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [102]:
                localctx = BedParser.SliceEnabledContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 549
                self.match(BedParser.T__101)
                self.state = 550
                self.match(BedParser.T__4)
                self.state = 551
                self.match(BedParser.BOOLEAN)
                self.state = 552
                self.match(BedParser.T__5)
                pass
            elif token in [103]:
                localctx = BedParser.SliceThicknessContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 553
                self.match(BedParser.T__102)
                self.state = 554
                self.match(BedParser.T__4)
                self.state = 555
                self.match(BedParser.NUMBER)
                self.state = 556
                self.match(BedParser.UNIT)
                self.state = 557
                self.match(BedParser.T__5)
                pass
            elif token in [104]:
                localctx = BedParser.SliceAxisContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 558
                self.match(BedParser.T__103)
                self.state = 559
                self.match(BedParser.T__4)
                self.state = 560
                self.match(BedParser.STRING)
                self.state = 561
                self.match(BedParser.T__5)
                pass
            elif token in [105]:
                localctx = BedParser.SlicePositionContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 562
                self.match(BedParser.T__104)
                self.state = 563
                self.match(BedParser.T__4)
                self.state = 564
                self.match(BedParser.NUMBER)
                self.state = 565
                self.match(BedParser.UNIT)
                self.state = 566
                self.match(BedParser.T__5)
                pass
            elif token in [106]:
                localctx = BedParser.SliceKeepOnlyContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 567
                self.match(BedParser.T__105)
                self.state = 568
                self.match(BedParser.T__4)
                self.state = 569
                self.match(BedParser.BOOLEAN)
                self.state = 570
                self.match(BedParser.T__5)
                pass
            elif token in [107]:
                localctx = BedParser.SlicePreservePackingContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 571
                self.match(BedParser.T__106)
                self.state = 572
                self.match(BedParser.T__4)
                self.state = 573
                self.match(BedParser.BOOLEAN)
                self.state = 574
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Statistical2dSectionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statistical2dProperty(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BedParser.Statistical2dPropertyContext)
            else:
                return self.getTypedRuleContext(BedParser.Statistical2dPropertyContext,i)


        def getRuleIndex(self):
            return BedParser.RULE_statistical2dSection

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatistical2dSection" ):
                listener.enterStatistical2dSection(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatistical2dSection" ):
                listener.exitStatistical2dSection(self)




    def statistical2dSection(self):

        localctx = BedParser.Statistical2dSectionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_statistical2dSection)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 577
            self.match(BedParser.T__107)
            self.state = 578
            self.match(BedParser.T__1)
            self.state = 580 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 579
                self.statistical2dProperty()
                self.state = 582 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==31 or _la==39 or ((((_la - 109)) & ~0x3f) == 0 and ((1 << (_la - 109)) & 31) != 0)):
                    break

            self.state = 584
            self.match(BedParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Statistical2dPropertyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return BedParser.RULE_statistical2dProperty

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class StatDomainWidthContext(Statistical2dPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.Statistical2dPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatDomainWidth" ):
                listener.enterStatDomainWidth(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatDomainWidth" ):
                listener.exitStatDomainWidth(self)


    class StatDomainHeightContext(Statistical2dPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.Statistical2dPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatDomainHeight" ):
                listener.enterStatDomainHeight(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatDomainHeight" ):
                listener.exitStatDomainHeight(self)


    class StatToleranceContext(Statistical2dPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.Statistical2dPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatTolerance" ):
                listener.enterStatTolerance(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatTolerance" ):
                listener.exitStatTolerance(self)


    class StatTargetPorosityContext(Statistical2dPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.Statistical2dPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatTargetPorosity" ):
                listener.enterStatTargetPorosity(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatTargetPorosity" ):
                listener.exitStatTargetPorosity(self)


    class StatSliceThicknessContext(Statistical2dPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.Statistical2dPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)
        def UNIT(self):
            return self.getToken(BedParser.UNIT, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatSliceThickness" ):
                listener.enterStatSliceThickness(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatSliceThickness" ):
                listener.exitStatSliceThickness(self)


    class StatMaxAttemptsContext(Statistical2dPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.Statistical2dPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatMaxAttempts" ):
                listener.enterStatMaxAttempts(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatMaxAttempts" ):
                listener.exitStatMaxAttempts(self)


    class StatSeedContext(Statistical2dPropertyContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a BedParser.Statistical2dPropertyContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(BedParser.NUMBER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatSeed" ):
                listener.enterStatSeed(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatSeed" ):
                listener.exitStatSeed(self)



    def statistical2dProperty(self):

        localctx = BedParser.Statistical2dPropertyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_statistical2dProperty)
        try:
            self.state = 617
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [109]:
                localctx = BedParser.StatDomainWidthContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 586
                self.match(BedParser.T__108)
                self.state = 587
                self.match(BedParser.T__4)
                self.state = 588
                self.match(BedParser.NUMBER)
                self.state = 589
                self.match(BedParser.UNIT)
                self.state = 590
                self.match(BedParser.T__5)
                pass
            elif token in [110]:
                localctx = BedParser.StatDomainHeightContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 591
                self.match(BedParser.T__109)
                self.state = 592
                self.match(BedParser.T__4)
                self.state = 593
                self.match(BedParser.NUMBER)
                self.state = 594
                self.match(BedParser.UNIT)
                self.state = 595
                self.match(BedParser.T__5)
                pass
            elif token in [31]:
                localctx = BedParser.StatTargetPorosityContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 596
                self.match(BedParser.T__30)
                self.state = 597
                self.match(BedParser.T__4)
                self.state = 598
                self.match(BedParser.NUMBER)
                self.state = 599
                self.match(BedParser.T__5)
                pass
            elif token in [111]:
                localctx = BedParser.StatToleranceContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 600
                self.match(BedParser.T__110)
                self.state = 601
                self.match(BedParser.T__4)
                self.state = 602
                self.match(BedParser.NUMBER)
                self.state = 603
                self.match(BedParser.T__5)
                pass
            elif token in [112]:
                localctx = BedParser.StatMaxAttemptsContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 604
                self.match(BedParser.T__111)
                self.state = 605
                self.match(BedParser.T__4)
                self.state = 606
                self.match(BedParser.NUMBER)
                self.state = 607
                self.match(BedParser.T__5)
                pass
            elif token in [113]:
                localctx = BedParser.StatSliceThicknessContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 608
                self.match(BedParser.T__112)
                self.state = 609
                self.match(BedParser.T__4)
                self.state = 610
                self.match(BedParser.NUMBER)
                self.state = 611
                self.match(BedParser.UNIT)
                self.state = 612
                self.match(BedParser.T__5)
                pass
            elif token in [39]:
                localctx = BedParser.StatSeedContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 613
                self.match(BedParser.T__38)
                self.state = 614
                self.match(BedParser.T__4)
                self.state = 615
                self.match(BedParser.NUMBER)
                self.state = 616
                self.match(BedParser.T__5)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





