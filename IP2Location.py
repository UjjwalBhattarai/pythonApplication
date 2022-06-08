import sys #importing modules
import struct
import socket
import re
import json
import os
import ipaddress
import binascii
from re import match

MAX_IPV4_RANGE = 4294967295
MAX_IPV6_RANGE = 340282366920938463463374607431768211455

_COUNTRY_POSITION             = (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2)
_REGION_POSITION              = (0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)
_CITY_POSITION                = (0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4)
_LATITUDE_POSITION            = (0, 0, 0, 0, 0, 5, 5, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5)
_LONGITUDE_POSITION           = (0, 0, 0, 0, 0, 6, 6, 0, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6)
_ZIPCODE_POSITION             = (0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 0, 7, 7, 7, 0, 7, 0, 7, 7, 7, 0, 7, 7)
_TIMEZONE_POSITION            = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 7, 8, 8, 8, 7, 8, 0, 8, 8, 8, 0, 8, 8)
_ISP_POSITION                 = (0, 0, 3, 0, 5, 0, 7, 5, 7, 0, 8, 0, 9, 0, 9, 0, 9, 0, 9, 7, 9, 0, 9, 7, 9, 9)
_DOMAIN_POSITION              = (0, 0, 0, 0, 0, 0, 0, 6, 8, 0, 9, 0, 10, 0, 10, 0, 10, 0, 10, 8, 10, 0, 10, 8, 10, 10)
_NETSPEED_POSITION            = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 11,0, 11,8, 11, 0, 11, 0, 11, 0, 11, 11)
_IDDCODE_POSITION             = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 12, 0, 12, 0, 12, 9, 12, 0, 12, 12)
_AREACODE_POSITION            = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10 ,13 ,0, 13, 0, 13, 10, 13, 0, 13, 13)
_WEATHERSTATIONCODE_POSITION  = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 14, 0, 14, 0, 14, 0, 14, 14)
_WEATHERSTATIONNAME_POSITION  = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 15, 0, 15, 0, 15, 0, 15, 15)
_MCC_POSITION                 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 16, 0, 16, 9, 16, 16)
_MNC_POSITION                 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 17, 0, 17, 10, 17, 17)
_MOBILEBRAND_POSITION         = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 18, 0, 18, 11, 18, 18)
_ELEVATION_POSITION           = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 19, 0, 19, 19)
_USAGETYPE_POSITION           = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 20, 20)
_ADDRESSTYPE_POSITION         = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21)
_CATEGORY_POSITION            = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 22)

if sys.version < '3':
    import urllib, httplib
    def urlencode(x):
        return urllib.urlencode(x)
    def httprequest(x, usessl):
        try:
            # conn = httplib.HTTPConnection("api.ip2location.com")
            if (usessl is True):
                conn = httplib.HTTPSConnection("api.ip2location.com")
            else:
                conn = httplib.HTTPConnection("api.ip2location.com")
            conn.request("GET", "/v2/?" + x)
            res = conn.getresponse()
            return json.loads(res.read())
        except:
            return None
    def u(x):
        return x.decode('utf-8')
    def b(x):
        return str(x)
else:
    import urllib.parse, http.client
    def urlencode(x):
        return urllib.parse.urlencode(x)
    def httprequest(x, usessl):
        try:
            # conn = http.client.HTTPConnection("api.ip2location.com")
            if (usessl is True):
                conn = http.client.HTTPSConnection("api.ip2location.com")
            else:
                conn = http.client.HTTPConnection("api.ip2location.com")
            conn.request("GET", "/v2/?" + x)
            res = conn.getresponse()
            return json.loads(res.read())
        except:
            return None
    def u(x):
        if isinstance(x, bytes):
            return x.decode()
        return x
    def b(x):
        if isinstance(x, bytes):
            return x
        return x.encode('ascii')
        
# Windows version of Python does not provide it
#          for compatibility with older versions of Windows.
if not hasattr(socket, 'inet_pton'):
    def inet_pton(t, addr):
        import ctypes
        a = ctypes.WinDLL('ws2_32.dll')
        in_addr_p = ctypes.create_string_buffer(b(addr))
        if t == socket.AF_INET:
            out_addr_p = ctypes.create_string_buffer(4)
        elif t == socket.AF_INET6:
            out_addr_p = ctypes.create_string_buffer(16)
        n = a.inet_pton(t, in_addr_p, out_addr_p)
        if n == 0:
            raise ValueError('Invalid address')
        return out_addr_p.raw
    socket.inet_pton = inet_pton

def is_ipv4(hostname):
    ip_parts = hostname.split('.')
    for i in range(0,len(ip_parts)):
        if int(ip_parts[i]) > 255:
            return False
    pattern = r'^([0-9]{1,3}[.]){3}[0-9]{1,3}$'
    if match(pattern, hostname) is not None:
        return 4
    return False

def is_ipv6(hostname):
    if ':' in hostname:
        return 6
    return False

def is_valid_ip(hostname):
    if is_ipv4(hostname) is not False or is_ipv6(hostname) is not False:
        return True
    else:
        return False

class IP2LocationRecord:
    ''' IP2Location record with all fields from the database '''
    ip = None
    country_short = None
    country_long = None
    region = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    city = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    isp = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    latitude = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    longitude = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    domain = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    zipcode = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    timezone = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    netspeed = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    idd_code = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    area_code = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    weather_code = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    weather_name = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    mcc = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    mnc = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    mobile_brand = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    elevation = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    usage_type = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    address_type = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."
    category = "This parameter is unavailable in selected .BIN data file. Please upgrade data file."

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

class IP2Location(object):
    ''' IP2Location database '''

    def __init__(self, filename=None,mode='FILE_IO'):
        ''' Creates a database object and opens a file if filename is given
            
        '''
        self.mode = mode
        
        if filename is not None:
            if os.path.isfile(filename) == False:
                raise ValueError("The database file does not seem to exist.")
        
        if filename:
            self.open(filename)

    def __enter__(self):
        if not hasattr(self, '_f') or self._f.closed:
            raise ValueError("Cannot enter context with closed file")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self, filename):
        ''' Opens a database file '''
        # Ensure old file is closed before opening a new one
        self.close()

        if (self.mode == 'SHARED_MEMORY'):
            import mmap
            db1 = open(filename, 'r+b')
            self._f = mmap.mmap(db1.fileno(), 0)
            db1.close()
            del db1
        elif (self.mode == 'FILE_IO'):
            self._f = open(filename, 'rb')
        else:
            raise ValueError("Invalid mode. Please enter either FILE_IO or SHARED_MEMORY.")
        self._dbtype = struct.unpack('B', self._f.read(1))[0]
        self._dbcolumn = struct.unpack('B', self._f.read(1))[0]
        self._dbyear = struct.unpack('B', self._f.read(1))[0]
        self._dbmonth = struct.unpack('B', self._f.read(1))[0]
        self._dbday = struct.unpack('B', self._f.read(1))[0]
        self._ipv4dbcount = struct.unpack('<I', self._f.read(4))[0]
        self._ipv4dbaddr = struct.unpack('<I', self._f.read(4))[0]
        self._ipv6dbcount = struct.unpack('<I', self._f.read(4))[0]
        self._ipv6dbaddr = struct.unpack('<I', self._f.read(4))[0]
        self._ipv4indexbaseaddr = struct.unpack('<I', self._f.read(4))[0]
        self._ipv6indexbaseaddr = struct.unpack('<I', self._f.read(4))[0]
        self._productcode = struct.unpack('B', self._f.read(1))[0]
        self._licensecode = struct.unpack('B', self._f.read(1))[0]
        self._databasesize = struct.unpack('B', self._f.read(1))[0]
        if (self._productcode != 1) :
            if (self._dbyear > 20 and self._productcode != 0) :
                self._f.close()
                del self._f
                raise ValueError("Incorrect IP2Location BIN file format. Please make sure that you are using the latest IP2Location BIN file.")


    def close(self):
        if hasattr(self, '_f'):
            # If there is file close it.
            self._f.close()
            del self._f

    def get_country_short(self, ip):
        ''' Get country_short '''
        rec = self.get_all(ip)
        return rec and rec.country_short
    def get_country_long(self, ip):
        ''' Get country_long '''
        rec = self.get_all(ip)
        return rec and rec.country_long
    def get_region(self, ip):
        ''' Get region '''
        rec = self.get_all(ip)
        return rec and rec.region
    def get_city(self, ip):
        ''' Get city '''
        rec = self.get_all(ip)
        return rec and rec.city
    def get_isp(self, ip):
        ''' Get isp '''
        rec = self.get_all(ip)
        return rec and rec.isp
    def get_latitude(self, ip):
        ''' Get latitude '''
        rec = self.get_all(ip)
        return rec and rec.latitude
    def get_longitude(self, ip):
        ''' Get longitude '''
        rec = self.get_all(ip)
        return rec and rec.longitude
    def get_domain(self, ip):
        ''' Get domain '''
        rec = self.get_all(ip)
        return rec and rec.domain
    def get_zipcode(self, ip):
        ''' Get zipcode '''
        rec = self.get_all(ip)
        return rec and rec.zipcode
    def get_timezone(self, ip):
        ''' Get timezone '''
        rec = self.get_all(ip)
        return rec and rec.timezone
    def get_netspeed(self, ip):
        ''' Get netspeed '''
        rec = self.get_all(ip)
        return rec and rec.netspeed
    def get_idd_code(self, ip):
        ''' Get idd_code '''
        rec = self.get_all(ip)
        return rec and rec.idd_code
    def get_area_code(self, ip):
        ''' Get area_code '''
        rec = self.get_all(ip)
        return rec and rec.area_code
    def get_weather_code(self, ip):
        ''' Get weather_code '''
        rec = self.get_all(ip)
        return rec and rec.weather_code
    def get_weather_name(self, ip):
        ''' Get weather_name '''
        rec = self.get_all(ip)
        return rec and rec.weather_name
    def get_mcc(self, ip):
        ''' Get mcc '''
        rec = self.get_all(ip)
        return rec and rec.mcc
    def get_mnc(self, ip):
        ''' Get mnc '''
        rec = self.get_all(ip)
        return rec and rec.mnc
    def get_mobile_brand(self, ip):
        ''' Get mobile_brand '''
        rec = self.get_all(ip)
        return rec and rec.mobile_brand
    def get_elevation(self, ip):
        ''' Get elevation '''
        rec = self.get_all(ip)
        return rec and rec.elevation
    def get_usage_type(self, ip):
        ''' Get usage_type '''
        rec = self.get_all(ip)
        return rec and rec.usage_type
    def get_address_type(self, ip):
        ''' Get address_type '''
        rec = self.get_all(ip)
        return rec and rec.address_type
    def get_category(self, ip):
        ''' Get category '''
        rec = self.get_all(ip)
        return rec and rec.category

    def get_all(self, addr):
        ''' Get the whole record with all fields read from the file

            Arguments:

            addr: IPv4 or IPv6 address as a string
     
            Returns IP2LocationRecord or None if address not found in file
        '''
        return self._get_record(addr)

    def find(self, addr):
        ''' Get the whole record with all fields read from the file

            Arguments:

            addr: IPv4 or IPv6 address as a string
     
            Returns IP2LocationRecord or None if address not found in file
            
            This function will be obselete in future.
        '''
        return self._get_record(addr)

    def _reads(self, offset):
        self._f.seek(offset - 1)
        n = struct.unpack('B', self._f.read(1))[0]
        # return u(self._f.read(n))
        if sys.version < '3':
            return str(self._f.read(n).decode('iso-8859-1').encode('utf-8'))
        else :
            return u(self._f.read(n).decode('iso-8859-1').encode('utf-8'))

    def _readi(self, offset):
        self._f.seek(offset - 1)
        # return struct.unpack('<I', self._f.read(4))[0]
        return struct.unpack('<L', self._f.read(4))[0]

    def _readf(self, offset):
        self._f.seek(offset - 1)
        return struct.unpack('<f', self._f.read(4))[0]

    def _readip(self, offset, ipv):
        if ipv == 4:
            return self._readi(offset)
        elif ipv == 6:
            a, b, c, d = self._readi(offset), self._readi(offset + 4), self._readi(offset + 8), self._readi(offset + 12) 
            return (d << 96) | (c << 64) | (b << 32) | a

    def _readips(self, offset, ipv):
        if ipv == 4:
            return socket.inet_ntoa(struct.pack('!L', self._readi(offset)))
        elif ipv == 6:
            return str(self._readip(offset, ipv))

    def _read_record(self, mid, ipv):
        rec = IP2LocationRecord()

        if ipv == 4:
            off = 0
            baseaddr = self._ipv4dbaddr
            dbcolumn_width = self._dbcolumn * 4 + 4
        elif ipv == 6:
            off = 12
            baseaddr = self._ipv6dbaddr
            dbcolumn_width = self._dbcolumn * 4

        def calc_off(what, mid):
            return baseaddr + mid * (self._dbcolumn * 4 + off) + off + 4 * (what[self._dbtype]-1)

        if (self.mode == 'SHARED_MEMORY'):
            # We can directly use slice notation to read content from mmap object. https://docs.python.org/3/library/mmap.html?highlight=mmap#module-mmap
            raw_positions_row = self._f[ (calc_off(_COUNTRY_POSITION, mid)) - 1 : (calc_off(_COUNTRY_POSITION, mid)) - 1 + dbcolumn_width]
        else:
            self._f.seek((calc_off(_COUNTRY_POSITION, mid)) - 1)
            raw_positions_row = self._f.read(dbcolumn_width)

        if self.original_ip != '':
            rec.ip = self.original_ip
        else:
            rec.ip = self._readips(baseaddr + (mid) * self._dbcolumn * 4, ipv)

        if _COUNTRY_POSITION[self._dbtype] != 0:
            rec.country_short = self._reads(struct.unpack('<I', raw_positions_row[0 : ((_COUNTRY_POSITION[self._dbtype]-1) * 4)])[0] + 1)
            rec.country_long =  self._reads(struct.unpack('<I', raw_positions_row[0 : ((_COUNTRY_POSITION[self._dbtype]-1) * 4)])[0] + 4)

        if _REGION_POSITION[self._dbtype] != 0:
            rec.region = self._reads(struct.unpack('<I', raw_positions_row[((_REGION_POSITION[self._dbtype]-1) * 4 - 4) : ((_REGION_POSITION[self._dbtype]-1) * 4)])[0] + 1)
        if _CITY_POSITION[self._dbtype] != 0:
            rec.city = self._reads(struct.unpack('<I', raw_positions_row[((_CITY_POSITION[self._dbtype]-1) * 4 - 4) : ((_CITY_POSITION[self._dbtype]-1) * 4)])[0] + 1)
        if _ISP_POSITION[self._dbtype] != 0:
            rec.isp = self._reads(struct.unpack('<I', raw_positions_row[((_ISP_POSITION[self._dbtype]-1) * 4 - 4) : ((_ISP_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _LATITUDE_POSITION[self._dbtype] != 0:
            rec.latitude = round(struct.unpack('<f', raw_positions_row[((_LATITUDE_POSITION[self._dbtype]-1) * 4 - 4) : ((_LATITUDE_POSITION[self._dbtype]-1) * 4)])[0], 6)
            rec.latitude = format(rec.latitude, '.6f')
        if _LONGITUDE_POSITION[self._dbtype] != 0:
            rec.longitude = round(struct.unpack('<f', raw_positions_row[((_LONGITUDE_POSITION[self._dbtype]-1) * 4 - 4) : ((_LONGITUDE_POSITION[self._dbtype]-1) * 4)])[0], 6)
            rec.longitude = format(rec.longitude, '.6f')

        if _DOMAIN_POSITION[self._dbtype] != 0:
            rec.domain = self._reads(struct.unpack('<I', raw_positions_row[((_DOMAIN_POSITION[self._dbtype]-1) * 4 - 4) : ((_DOMAIN_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _ZIPCODE_POSITION[self._dbtype] != 0:
            rec.zipcode = self._reads(struct.unpack('<I', raw_positions_row[((_ZIPCODE_POSITION[self._dbtype]-1) * 4 - 4) : ((_ZIPCODE_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _TIMEZONE_POSITION[self._dbtype] != 0:
            rec.timezone = self._reads(struct.unpack('<I', raw_positions_row[((_TIMEZONE_POSITION[self._dbtype]-1) * 4 - 4) : ((_TIMEZONE_POSITION[self._dbtype]-1) * 4)])[0] + 1)
                
        if _NETSPEED_POSITION[self._dbtype] != 0:
            rec.netspeed = self._reads(struct.unpack('<I', raw_positions_row[((_NETSPEED_POSITION[self._dbtype]-1) * 4 - 4) : ((_NETSPEED_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _IDDCODE_POSITION[self._dbtype] != 0:
            rec.idd_code = self._reads(struct.unpack('<I', raw_positions_row[((_IDDCODE_POSITION[self._dbtype]-1) * 4 - 4) : ((_IDDCODE_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _AREACODE_POSITION[self._dbtype] != 0:
            rec.area_code = self._reads(struct.unpack('<I', raw_positions_row[((_AREACODE_POSITION[self._dbtype]-1) * 4 - 4) : ((_AREACODE_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _WEATHERSTATIONCODE_POSITION[self._dbtype] != 0:
            rec.weather_code = self._reads(struct.unpack('<I', raw_positions_row[((_WEATHERSTATIONCODE_POSITION[self._dbtype]-1) * 4 - 4) : ((_WEATHERSTATIONCODE_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _WEATHERSTATIONNAME_POSITION[self._dbtype] != 0:
            rec.weather_name = self._reads(struct.unpack('<I', raw_positions_row[((_WEATHERSTATIONNAME_POSITION[self._dbtype]-1) * 4 - 4) : ((_WEATHERSTATIONNAME_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _MCC_POSITION[self._dbtype] != 0:
            rec.mcc = self._reads(struct.unpack('<I', raw_positions_row[((_MCC_POSITION[self._dbtype]-1) * 4 - 4) : ((_MCC_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _MNC_POSITION[self._dbtype] != 0:
            rec.mnc = self._reads(struct.unpack('<I', raw_positions_row[((_MNC_POSITION[self._dbtype]-1) * 4 - 4) : ((_MNC_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _MOBILEBRAND_POSITION[self._dbtype] != 0:
            rec.mobile_brand = self._reads(struct.unpack('<I', raw_positions_row[((_MOBILEBRAND_POSITION[self._dbtype]-1) * 4 - 4) : ((_MOBILEBRAND_POSITION[self._dbtype]-1) * 4)])[0] + 1)
                
        if _ELEVATION_POSITION[self._dbtype] != 0:
            rec.elevation = self._reads(struct.unpack('<I', raw_positions_row[((_ELEVATION_POSITION[self._dbtype]-1) * 4 - 4) : ((_ELEVATION_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _USAGETYPE_POSITION[self._dbtype] != 0:
            rec.usage_type = self._reads(struct.unpack('<I', raw_positions_row[((_USAGETYPE_POSITION[self._dbtype]-1) * 4 - 4) : ((_USAGETYPE_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _ADDRESSTYPE_POSITION[self._dbtype] != 0:
            rec.address_type = self._reads(struct.unpack('<I', raw_positions_row[((_ADDRESSTYPE_POSITION[self._dbtype]-1) * 4 - 4) : ((_ADDRESSTYPE_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        if _CATEGORY_POSITION[self._dbtype] != 0:
            rec.category = self._reads(struct.unpack('<I', raw_positions_row[((_CATEGORY_POSITION[self._dbtype]-1) * 4 - 4) : ((_CATEGORY_POSITION[self._dbtype]-1) * 4)])[0] + 1)

        return rec

    def __iter__(self):
        low, high = 0, self._ipv4dbcount
        while low <= high:
            yield self._read_record(low, 4)
            low += 1

        low, high = 0, self._ipv6dbcount
        while low <= high:
            yield self._read_record(low, 6)
            low += 1

    def _ip2no(self, addr):
        no = 0
        block = addr.split('.')
        no = block[3]
        no = no + block[2] * 256
        no = no + block[1] * 256 * 256
        no = no + block[0] * 256 * 256 * 256
        return int(no)

    def _parse_addr(self, addr): 
        ''' Parses address and returns IP version. Raises exception on invalid argument '''
        ipv = 0
        ipnum = -1
        if is_ipv6(addr) == 6:
            try:
                ipv = 6
                # ipnum = int(int(ipaddress.IPv6Address(addr)).__str__())
                a, b = struct.unpack('!QQ', socket.inet_pton(socket.AF_INET6, addr))
                ipnum = (a << 64) | b
                '''
                # Convert ::FFFF:x.y.z.y to IPv4
                if addr.lower().startswith('::ffff:'):
                    try:
                        socket.inet_pton(socket.AF_INET, addr)
                        ipv = 4
                    except:
                        # reformat ipv4 address in ipv6 
                        if ((ipnum >= 281470681743360) and (ipnum <= 281474976710655)):
                            ipv = 4
                            ipnum = ipnum - 281470681743360
                        else:
                            ipv = 6
                else:
                    #reformat 6to4 address to ipv4 address 2002:: to 2002:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF
                    if ((ipnum >= 42545680458834377588178886921629466624) and (ipnum <= 42550872755692912415807417417958686719)):
                        ipv = 4
                        ipnum = ipnum >> 80
                        ipnum = ipnum % 4294967296
                    #reformat Teredo address to ipv4 address 2001:0000:: to 2001:0000:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:
                    elif ((ipnum >= 42540488161975842760550356425300246528) and (ipnum <= 42540488241204005274814694018844196863)):
                        ipv = 4
                        ipnum = ~ ipnum
                        ipnum = ipnum % 4294967296
                    else:
                        ipv = 6
                '''
                #reformat 6to4 address to ipv4 address 2002:: to 2002:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF
                if ((ipnum >= 42545680458834377588178886921629466624) and (ipnum <= 42550872755692912415807417417958686719)):
                    ipv = 4
                    ipnum = ipnum >> 80
                    ipnum = ipnum % 4294967296
                #reformat Teredo address to ipv4 address 2001:0000:: to 2001:0000:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:
                elif ((ipnum >= 42540488161975842760550356425300246528) and (ipnum <= 42540488241204005274814694018844196863)):
                    ipv = 4
                    ipnum = ~ ipnum
                    ipnum = ipnum % 4294967296
                # reformat ipv4 address in ipv6 
                elif ((ipnum >= 281470681743360) and (ipnum <= 281474976710655)):
                    ipv = 4
                    ipnum = ipnum - 281470681743360
                else:
                    ipv = 6
            except (socket.error, OSError, ValueError):
                ipv = 0
                ipnum = -1
        elif is_ipv4(addr) == 4 and '256' not in addr:
            try:
                # ipnum = int(ipaddress.IPv4Address(addr))
                ipnum = struct.unpack('!L', socket.inet_pton(socket.AF_INET, addr))[0]
                ipv = 4
            except (socket.error, OSError, ValueError):
                ipv = 0
                ipnum = -1
        return ipv, ipnum
        
    def _get_record(self, ip):
        # global original_ip
        self.original_ip = ip
        low = 0
        # ipv = self._parse_addr(ip)
        # ipv = self._parse_addr(ip)[0]
        # ipnum = self._parse_addr(ip)[1]
        ipv, ipnum = self._parse_addr(ip)
        if ipv == 0:
            rec = IP2LocationRecord()
            rec.country_short = "INVALID IP ADDRESS"
            rec.country_long = "INVALID IP ADDRESS"
            rec.region = "INVALID IP ADDRESS"
            rec.city = "INVALID IP ADDRESS"
            rec.isp = "INVALID IP ADDRESS"
            rec.latitude = "INVALID IP ADDRESS"
            rec.longitude = "INVALID IP ADDRESS"
            rec.domain = "INVALID IP ADDRESS"
            rec.zipcode = "INVALID IP ADDRESS"
            rec.timezone = "INVALID IP ADDRESS"
            rec.netspeed = "INVALID IP ADDRESS"
            rec.idd_code = "INVALID IP ADDRESS"
            rec.area_code = "INVALID IP ADDRESS"
            rec.weather_code = "INVALID IP ADDRESS"
            rec.weather_name = "INVALID IP ADDRESS"
            rec.mcc = "INVALID IP ADDRESS"
            rec.mnc = "INVALID IP ADDRESS"
            rec.mobile_brand = "INVALID IP ADDRESS"
            rec.elevation = "INVALID IP ADDRESS"
            rec.usage_type = "INVALID IP ADDRESS"
            rec.address_type = "INVALID IP ADDRESS"
            rec.category = "INVALID IP ADDRESS"
            return rec
        else:
            if ipv == 4:
                # ipno = struct.unpack('!L', socket.inet_pton(socket.AF_INET, ip))[0]
                if (ipnum == MAX_IPV4_RANGE):
                    ipno = ipnum - 1
                else:
                    ipno = ipnum
                off = 0
                baseaddr = self._ipv4dbaddr
                high = self._ipv4dbcount
                if self._ipv4indexbaseaddr > 0:
                    indexpos = ((ipno >> 16) << 3) + self._ipv4indexbaseaddr
                    low = self._readi(indexpos)
                    high = self._readi(indexpos + 4)

            elif ipv == 6:
                if self._ipv6dbcount == 0:
                    # raise ValueError('Please use IPv6 BIN file for IPv6 Address.')
                    rec = IP2LocationRecord()
                    rec.country_short = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.country_long = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.region = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.city = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.isp = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.latitude = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.longitude = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.domain = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.zipcode = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.timezone = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.netspeed = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.idd_code = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.area_code = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.weather_code = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.weather_name = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.mcc = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.mnc = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.mobile_brand = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.elevation = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.usage_type = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.address_type = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    rec.category = "IPV6 ADDRESS MISSING IN IPV4 BIN"
                    return rec
                # a, b = struct.unpack('!QQ', socket.inet_pton(socket.AF_INET6, ip))
                # ipno = (a << 64) | b
                if (ipnum == MAX_IPV6_RANGE):
                    ipno = ipnum - 1
                else:
                    ipno = ipnum
                off = 12
                baseaddr = self._ipv6dbaddr
                high = self._ipv6dbcount
                if self._ipv6indexbaseaddr > 0:
                    indexpos = ((ipno >> 112) << 3) + self._ipv6indexbaseaddr
                    low = self._readi(indexpos)
                    high = self._readi(indexpos + 4)

            while low <= high:
                mid = int((low + high) / 2)
                ipfrom = self._readip(baseaddr + (mid) * (self._dbcolumn * 4 + off), ipv)
                ipto = self._readip(baseaddr + (mid + 1) * (self._dbcolumn * 4 + off), ipv)

                if ipfrom <= ipno < ipto:
                    return self._read_record(mid, ipv)
                else:
                    if ipno < ipfrom:
                        high = mid - 1
                    else:
                        low = mid + 1

class IP2LocationWebService(object):
    ''' IP2Location web service '''
    def __init__(self,apikey,package,usessl=True):
        if ((re.match(r"^[0-9A-Z]{10}$", apikey) == None) and (apikey != 'demo')):
            raise ValueError("Please provide a valid IP2Location web service API key.")
        if (re.match(r"^WS[0-9]+$", package) == None):
            package = 'WS1'
        self.apikey = apikey
        self.package = package
        self.usessl = usessl
    
    def lookup(self,ip,addons=[],language='en'):
        '''This function will look the given IP address up in IP2Location web service.'''
        parameters = urlencode((("key", self.apikey), ("ip", ip), ("package", self.package), ("addon", ','.join(addons)), ("lang", language)))
        response = httprequest(parameters, self.usessl)
        if (response == None):
            return False
        # if ('response' in response):
        if (('response' in response) and (response['response'] != 'OK')):
            raise IP2LocationAPIError(response['response'])
        return response

    def getcredit(self):
        '''Get the remaing credit in your IP2Location web service account.'''
        parameters = urlencode((("key", self.apikey), ("check", True)))
        response = httprequest(parameters, self.usessl)
        if (response == None):
            return 0
        if ('response' in response is False):
            return 0
        return response['response']
  
class IP2LocationAPIError(Exception):
    """Raise for IP2Location API Error Message"""

class IP2LocationIPTools(object):

    def is_ipv4(self, ip):
        if '.' in ip:
            ip_parts = ip.split('.')
            if len(ip_parts) == 4:
                for i in range(0,len(ip_parts)):
                    if str(ip_parts[i]).isdigit():
                        if int(ip_parts[i]) > 255:
                            return False
                    else:
                        return False
                pattern = r'^([0-9]{1,3}[.]){3}[0-9]{1,3}$'
                if match(pattern, ip) is not None:
                    return True
            else:
                return False
        else:
            return False
        return False

    def is_ipv6(self, ip):
        try:
            socket.inet_pton(socket.AF_INET6, ip)
        except socket.error:  # not a valid address
            return False
        return True
    
    def ipv4_to_decimal(self, ip):
        try:
            ipnum = struct.unpack('!L', socket.inet_pton(socket.AF_INET, ip))[0]
        except (socket.error, OSError, ValueError):
            # ipnum = -1
            return
        return ipnum
    
    def decimal_to_ipv4(self, decimal):
        if str(decimal).isdigit() is False:
            return
        if (int(decimal) > 4294967295):
            return
        else:
            return (socket.inet_ntoa(struct.pack('!I', int(decimal))))
    
    def ipv6_to_decimal(self, ip):
        if self.is_ipv6(ip) is False:
            return
        return(int(ipaddress.ip_address(u(ip))))
    
    def decimal_to_ipv6(self, decimal):
        if str(decimal).isdigit() is False:
            return
        result = ipaddress.IPv6Address(int(decimal))
        if (result.ipv4_mapped != None):
            return('::ffff:' + str(result.ipv4_mapped))
        else:
            return str(result)
    
    def ipv4_to_cidr(self, from_ip, to_ip):
        if self.is_ipv4(from_ip) is False:
            return
        if self.is_ipv4(to_ip) is False:
            return
        startip = ipaddress.IPv4Address(u(from_ip))
        endip = ipaddress.IPv4Address(u(to_ip))
        ar = [ipaddr for ipaddr in ipaddress.summarize_address_range(startip, endip)]
        ar1 = []
        for i in range(len(ar)):
            ar1.append(str(ar[i]))
        return (ar1)
    
    def ipv6_to_cidr(self, from_ip, to_ip):
        if self.is_ipv6(from_ip) is False:
            return
        if self.is_ipv6(to_ip) is False:
            return
        startip = ipaddress.IPv6Address(u(from_ip))
        endip = ipaddress.IPv6Address(u(to_ip))
        ar = [ipaddr for ipaddr in ipaddress.summarize_address_range(startip, endip)]
        ar1 = []
        for i in range(len(ar)):
            ar1.append(str(ar[i]))
        return (ar1)
    
    def cidr_to_ipv4(self, cidr):
        if '/' not in cidr:
            return
        net=ipaddress.ip_network(u(cidr))
        return({"ip_start": str(net[0]), "ip_end": str(net[-1])})
    
    def cidr_to_ipv6(self, cidr):
        if '/' not in cidr:
            return
        parts = cidr.split('/')
        hexstartaddress = binascii.hexlify(socket.inet_pton(socket.AF_INET6, parts[0]))
        if (len(hexstartaddress) < 16):
            hexstartaddress = hexstartaddress.zfill(16-hexstartaddress.len())
        bits = 128 - int(parts[1])
        hexlastaddress = hexstartaddress
        pos = 31
        while (bits > 0):
            int_value = int(hexlastaddress[pos:pos+1], 16)
            # new = binascii.hexlify((int_value | (pow(2, min(4, bits)) - 1)).to_bytes(1, 'big'))
            new = binascii.hexlify((int_value | (pow(2, min(4, bits)) - 1)).to_bytes(1, 'little'))[1:]
            hexlastaddresslist = list(u(hexlastaddress))
            hexlastaddresslist[pos] = u(new)
            string_hexlastaddresslist = [str(int) for int in hexlastaddresslist] 
            hexlastaddress = ''.join(string_hexlastaddresslist)
            bits = bits - 4
            pos = pos - 1
        binlastaddress = binascii.unhexlify(b(hexlastaddress))
        return({"ip_start": self.expand_ipv6(parts[0]), "ip_end": self.expand_ipv6(socket.inet_ntop(socket.AF_INET6, binlastaddress))})
    
    def compressed_ipv6(self, ip):
        if self.is_ipv6(ip) is False:
            return
        return ((ipaddress.IPv6Address(u(ip)).compressed))
    
    def expand_ipv6(self, ip):
        if self.is_ipv6(ip) is False:
            return
        return ((ipaddress.IPv6Address(u(ip)).exploded))

