#!/usr/bin/env python3
from __future__ import print_function # sphinx is using python2.7
__doc__ ='''
Fetch GNSS products in GCORE format with file names suitable for gd2e.py

Output to a directory, create it if it doesn't exist.

For just cloning all or part of a JPL_GNSS_Products directory ( which can also be 
used as input to gd2e.py ) to a local disk, wget maybe more appropriate. See, example.

If the time span (-startTime, -endTime), requires multiple data from multiple days,
pos and tdp files will be cat'd together leaving off the midnight point from the earlier
file and including 00:00 from the next file. A geop file is constructed from IERS buletin A
using geop.py. The wlpb file will be empty.
'''

Epilog = '''

:Examples:
::

    fetchGNSSproducts.py -s 2015-06-01
    Fetched GNSS products Found GOA style. Source: ftp://sideshow.jpl.nasa.gov/pub/JPL_GPS_Products/Final. recovered using files with date labels 2015-06-01 to 2015-06-01.
    ls GNSSinitValues/
    GNSSinitValues:
    GNSS.eo    GNSS.meta  GNSS.pcm   GNSS.pos   GNSS.tdp   GNSS.wlpb  

    fetchGNSSproducts.py -s 2015-06-01 -tar flinnRConverted
    Fetched GNSS products Found GOA style. Source: ftp://sideshow.jpl.nasa.gov/pub/JPL_GPS_Products/Final. recovered using files with date labels 2015-06-01 to 2015-06-01.
    ls flinnRConverted/
    flinnRConverted:
    GNSS.ant   GNSS.eo    GNSS.pcm   GNSS.meta GNSS.pos   GNSS.tdp   GNSS.wlpb  

    # Grap the GipsyX "Final" products from 2017-11-18 using wget
    wget 'ftp://sideshow.jpl.nasa.gov/pub/JPL_GNSS_Products/Final/2017/2017-11-18*.gz' > & wget.log
    ls
    2017-11-18.eo.gz          2017-11-18_nf.stacov.gz   2017-11-18_nnr.stacov.gz  2017-11-18.shadhist.gz 
    2017-11-18_hr.tdp.gz      2017-11-18_nf.tdp.gz      2017-11-18_nnr.tdp.gz     2017-11-18.stacov.gz 
    2017-11-18.meta.gz        2017-11-18_nf.wlpb.gz     2017-11-18_nnr.wlpb.gz    2017-11-18.tdp.gz 
    2017-11-18_nf.eo.gz       2017-11-18_nnr.eo.gz      2017-11-18_nnr.x.gz       2017-11-18.wlpb.gz 
    2017-11-18_nf_hr.tdp.gz   2017-11-18_nnr_hr.tdp.gz  2017-11-18.pcm.gz         2017-11-18.x.gz 
    2017-11-18_nf.pos.gz      2017-11-18_nnr.pos.gz     2017-11-18.pos.gz         wget.log 


    # or grab the whole month, see man wget for additional options you may want.
    wget 'ftp://sideshow.jpl.nasa.gov/pub/JPL_GNSS_Products/Final/2017/2017-11-*.gz' > & wget.log  

    # To grab a month of data for https protocol the wget command must be modified slightly
    wget -r -l1 -nd https://sideshow.jpl.nasa.gov/pub/JPL_GNSS_Products/Final/2017/ -A '2017-11-*.gz' > & wget.log 


Keywords: GNSSproducts
'''

__author__   = 'Willy Bertiger'

import sys, os,  argparse

sys.path.insert(0, "{}/lib/python{}.{}".format(os.environ['GCOREBUILD'], \
                    sys.version_info[0], sys.version_info[1]))

#from gcore.stringToObj import Date2Sec
from gcore.GNSSproducts import FetchGNSSproducts
from gcore.gd2eUtilities import GnssProductsInput

def _getParser():   # our special code to use sphinx argparse requires argparse be wrap with this exact funtion name.
    argParser = argparse.ArgumentParser(description= __doc__, epilog=Epilog, 
                                        formatter_class=argparse.RawDescriptionHelpFormatter )

    argParser.add_argument('-startTime',action='store',required=True,nargs='+',default=None,metavar='startTime',type=int,
                               help='Start of the orbit, clock ... sequence in J2000 sec. ')

    argParser.add_argument('-endTime',action='store',required=False,nargs='+',default=None, metavar='endTime',type=int,
                               help='''End of the orbit, clock,... sequence in J2000 sec. Default: startTime + 1 day
                               ''')
    argParser.add_argument('-targetDir', nargs='?', metavar='targetDir', default='GNSSinitValues',help='''
                                A directory to output the results. Created if it does not exist.
                                Default: GNSSinitValues
                              ''')

    gnssProductsDefault = 'https://sideshow.jpl.nasa.gov/pub/JPL_GNSS_Products/Final'
    argParser.add_argument('-GNSSproducts', metavar='dir|url',nargs='+', action=GnssProductsInput,
                           default=gnssProductsDefault, help='''
                            A directory or URL containing the dataBase of GNSS products. This 
                            top level url or directory should contain sub-direcories YYYY, for 
                            each year. It maybe either gcore formatted or GOA formatted, see
                            {}
                            Default: {}, fetchGNSSproducts.py will create a sub-directory, GNSSinitValues with files:
                            GNSS.meta, GNSS.eo, GNSS.pcm, GNSS.pos, GNSS.tdp, GNSS.wlpb. Note when fetching legacy
                            products the meta file will only contain antenna information.
                           {}. See -prodType.
                           '''.format(os.environ['GCORE']+'/file_formats/JPL_GNSSproducts', gnssProductsDefault,
                                      GnssProductsInput.shortCutHelp) )

    argParser.add_argument('-prodType', metavar='nf|nnr|fid', default='fid', help='''
                                type of products to fetch. Can be fiducial-free (nf), no-net-rotation (nnr) or fiducial (fid).
                                Note that this only applies if you are fetching final-type products. Default is fid.''')

    argParser.add_argument('-hr24', action='store_true',default=False, help='''Assume the database consists of 
                           24-hr files instead of the standard 30-hour files. Default: False, 30-hr database                                          ''')
    
    argParser.add_argument('-HighRate', action='store_true',
                           help='If set, high-rate products will be fetched.')
    
    argParser.add_argument('-quat', action='store_true',
                           help='''If set, an attempt is made to fetch quat products.
                               Nothing will happen if GNSSproducts is set to a GOA formatted area.
                           ''')
    argParser.add_argument('-makeShadowFile', action='store_true',
                           help='''If set, an attempt is made to make a shadow file in -targetDir from
                               the final GNSS.pos file. Useful if e.g. you want to run many PPPs from 
                               a single set of products because it can save time to just read a shadow 
                               file up front rather than creating it on the fly for each PPP run.
                           ''')
    argParser.add_argument('-intersection', action='store_true',
                           help='''If set, only the intersection of satellites present on all
                               days of every pos file required to cover the requested date span
                               will be included in the file. By default, every satellite available
                               at any time is included.''')

    return argParser

if __name__ == '__main__':
    args = _getParser().parse_args()

    if not args.endTime: args.endTime = args.startTime + 86400

    fetchGNSSproducts = FetchGNSSproducts()
    fetchGNSSproducts.targetDir = args.targetDir
    fetchGNSSproducts.repository = args.GNSSproducts
    fetchGNSSproducts.highRate = args.HighRate
    fetchGNSSproducts.quat = args.quat
    fetchGNSSproducts.prodType = args.prodType
    fetchGNSSproducts.hr24=args.hr24

    try:
        productStr, satList = fetchGNSSproducts.makeFiles(args.startTime[0],args.endTime[0],
                                                      intersection=args.intersection,
                                                      shad = args.makeShadowFile)
    except Exception as e:
        print('Fatal error: {}'.format(e), file=sys.stderr)
        sys.exit(1)
    print('Fetched GNSS products {}'.format(productStr))