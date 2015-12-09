#!/usr/bin/python

# GoProHero.py
# Josh Villbrandt <josh@javconcepts.com>, Blair Gagnon <blairgagnon@gmail.com>
# August 2013 - November 2014
# Modified by Alexis Morin <mail@alexismorin.com>

import logging
import socket
import unicodedata
from colorama import Fore

# urllib support for Python 2 and Python 3
# try:
#     from urllib.request import urlopen, HTTPError, URLError
# except ImportError:
import urllib3

# attempt imports for image() function
try:
    import cv2
    from PIL import Image
    import StringIO
    import base64
except ImportError:
    pass


class GoProHero4:
    @classmethod
    def config(self):
        return {
            'status': GoProHero.statusMatrix,
            'command': GoProHero.commandMatrix
        }

    @classmethod
    def _hexToDec(self, val):
        return int(val, 16)

    @classmethod
    def _splitByControlCharacters(self, val):
        # extract non-control characters
        output = []
        s = ''
        for c in unicode(val):
            if unicodedata.category(c)[0] == 'C':
                if len(s) > 0:
                    # start a new string if we found a control character
                    output.append(str(s))
                    s = ''
            else:
                s += c

        # clean up any left over string
        if len(s) > 0:
            output.append(str(s))

        # return extracts strings
        return output

    @classmethod
    def _extractModel(self, val):
        parts = self._splitByControlCharacters(val.decode('hex'))
        if len(parts) > 0:
            # the first two chunks of 'HD4.02.01.02.00'
            return '.'.join(parts[0].split('.')[0:2])
        else:
            return None

    @classmethod
    def _extractFirmware(self, val):
        parts = self._splitByControlCharacters(val.decode('hex'))
        if len(parts) > 0:
            # everything except the first two chunks of 'HD4.02.01.02.00'
            return '.'.join(parts[0].split('.')[2:])
        else:
            return None

    @classmethod
    def _extractName(self, val):
        parts = self._splitByControlCharacters(val.decode('hex'))
        if len(parts) > 1:
            return parts[1]
        else:
            return None

    def _statusURL(self):
        return 'http://{}/camera/se'.format(self._ip)

    def _originalStatusURL(self, command):
        return 'http://{}/{}?t={}'.format(self._ip, command, 'imagination')

    def _commandURL(self, command, value):
        #print command
        commandURI = self.commandMatrix[command]
        options = self.commandMatrix[command]['translate']
        cmd = self.commandMatrix[command]['cmd']

        if( type(value) is not int):
            for key in options:
                if (value == options[key]):
                    value = key
        #if we passed an int or None, run it as is
        # (deleteall uses None)

        print value

        #print options
        return 'http://{}/gp/gpControl/{}{}'.format(
            self._ip, cmd, value)

    def _previewURL(self):
        return 'http://{}:8080/live/amba.m3u8'.format(self._ip)

    originalStatusMatrix = {
        'bacpac/se': {
            'power': {
                'a': 18,
                'b': 20,
                'translate': {
                    '00': 'sleeping',
                    '01': 'on'
                }
            }
        },
        'camera/se': {
            'preview': {
                'a': 37,
                'b': 38,
                'translate': {
                    '0': 'off',
                    '1': 'on'
                }
            },
            'batt1': {
                'a': 38,
                'b': 40,
                'translate': '_hexToDec'
            }
        },
        'camera/sx': {  # the first 62 bytes of sx are almost the same as se
            'mode': {
                'a': 2,
                'b': 4,
                'translate': {
                    '00': 'video',
                    '01': 'still',
                    '02': 'burst',
                    '03': 'timelapse',
                    '07': 'settings'
                }
            },
            'defaultmode': {
                'a': 6,
                'b': 8,
                'translate': {
                    '00': 'video',
                    '01': 'still',
                    '02': 'burst',
                    '03': 'timelapse'
                }
            },
            'spotmeter': {
                'a': 8,
                'b': 10,
                'translate': {
                    '00': 'off',
                    '01': 'on'
                }
            },
            'timelapseinterval': {
                'a': 10,
                'b': 12,
                'translate': '_hexToDec'
            },
            'autooff': {
                'a': 12,
                'b': 14,
                'translate': {
                    '00': 'never',
                    '01': '1 minute',
                    '02': '2 minutes',
                    '03': '5 minutes'
                }
            },
            'fov': {
                'a': 14,
                'b': 16,
                'translate': {
                    '00': '170',
                    '01': '127',
                    '02': '90'
                }
            },
            'picres': {
                'a': 17,
                'b': 18,
                'translate': {
                    '3': '5MP med',
                    '6': '7MP med',
                    '4': '7MP wide',
                    '5': '12MP wide'
                }
            },
            'minselapsed': {
                'a': 26,
                'b': 28,
                'translate': '_hexToDec'
            },
            'secselapsed': {
                'a': 28,
                'b': 30,
                'translate': '_hexToDec'
            },
            'orientation': {
                'a': 37,
                'b': 38,
                'translate': {
                    # looks like this really should just be the third bit
                    '0': 'up',
                    '4': 'down'
                }
            },
            'charging': {
                'a': 39,
                'b': 40,
                'translate': {
                    '2': 'no',  # 2 only shows up temporarily
                    '3': 'no',
                    '4': 'yes'
                }
            },
            'picsremaining': {
                'a': 42,
                'b': 46,
                'translate': '_hexToDec'
            },
            'npics': {
                'a': 46,
                'b': 50,
                'translate': '_hexToDec'
            },
            'minsremaining': {
                'a': 50,
                'b': 54,
                'translate': '_hexToDec'
            },
            'nvids': {
                'a': 54,
                'b': 58,
                'translate': '_hexToDec'
            },
            'record': {
                'a': 58,
                'b': 60,
                'translate': {
                    '00': 'off',
                    '01': 'on'
                }
            },
            'lowlight': {
                'a': 60,
                'b': 61,
                'translate': {
                    '0': 'off',
                    '4': 'on'
                }
            },
            'protune': {
                'a': 61,
                'b': 62,
                'translate': {
                    '0': 'off',  # seems to be only while in the menu
                    '2': 'on',  # seems to be only while in the menu
                    '4': 'off',
                    '6': 'on'
                }
            },
            'whitebalance': {
                'a': 69,
                'b': 70,
                'translate': {
                    '0': 'auto',
                    '1': '3000K',
                    '2': '5500K',
                    '3': '6500K',
                    '4': 'raw'
                }
            },
            'looping': {
                'a': 74,
                'b': 76,
                'translate': {
                    '00': 'off',
                    '01': '5 minutes',
                    '02': '20 minutes',
                    '03': '60 minutes',
                    '04': '120 minutes',
                    '05': 'max'
                }
            },
            'batt2': {
                'a': 90,
                'b': 92,
                'translate': '_hexToDec'
            },
            'overheated': {  # experimental
                'a': 92,
                'b': 93,
                'translate': {
                    '0': 'false',
                    '4': 'true'
                }
            },
            'attachment': {
                'a': 93,
                'b': 94,
                'translate': {
                    '0': 'none',
                    '4': 'LCD',
                    '8': 'battery'
                }
            },
            'vidres': {
                'a': 100,
                'b': 102,
                'translate': {
                    '00': 'WVGA',
                    '01': '720p',
                    '02': '960p',
                    '03': '1080p',
                    '04': '1440p',
                    '05': '2.7K',
                    '06': '2.7K 17:9 Cinema',
                    '07': '4K',
                    '08': '4K 17:9 Cinema',
                    '09': '1080p SuperView',
                    '0a': '720p SuperView'
                }
            },
            'fps': {
                'a': 102,
                'b': 104,
                'translate': {
                    '00': '12',
                    '01': '15',
                    '02': '24',
                    '03': '25',
                    '04': '30',
                    '05': '48',
                    '06': '50',
                    '07': '60',
                    '08': '100',
                    '09': '120',
                    '0a': '240'
                }
            }
        },
        'camera/cv': {
            'name': {
                'translate': '_extractName'
            },
            'model': {
                'translate': '_extractModel'
            },
            'firmware': {
                'translate': '_extractFirmware'
            }
        }
    }

    statusMatrix = {
        0: {}, #unknown
        1: { 'current_mode':{
                0 : 'video',
                1 : 'photo',
                2 : 'multishot',
                3 : 'timelapse',
                4 : 'nightlapse',
                7 : 'settings'
            }
        },
        2:{}, # unknown
        3:{'startup_mode':{
                0: 'video',
                1: 'photo',
                2: 'burst',
                3: 'timelapse'
            }
        },
        4: {'spot_meter': {
                0: 'off',
                1: 'on'
            }
        },
        5: {'curr_timelapse_interval': 'variable'},
        6: {'auto_power_off':{
            0: 'never',
            1: '60sec',
            2: '120sec',
            3: '300sec'
        }}
    }

    commandMatrix = {
        'mode':{
        'cmd' : 'command/mode?p=',
        'translate':{
            0 : 'video',
            1 : 'photo',
            2 : 'multishot'}
        },
        'protune':{
        'cmd' : 'setting/10/',
        'translate':{
            0 : 'off',
            1 : 'on'}
        },
        'photoresolution':{
        'cmd' : 'setting/17/',
        'translate':{
            0 : '12MPWide',
            1 : '7MPWide',
            2 : '7MPMed',
            3 : '5MPWide'}
        },
        'fps':{
        'cmd' : 'setting/3/',
        'translate' : {
            0 : 'setting1',
            1 : 'setting2',
            2 : 'setting3',
            3 : 'setting4',
            4 : 'setting5',
            5 : 'setting6',
            6 : 'setting7'}
        },
        'videoresolution':{
        'cmd' : 'setting/2/',
        'translate' : {
            1 : '4K',
            2 : '4KSuperview',
            4 : '2.7K',
            5 : '2.7KSuperview',
            6 : '2.7K4:3',
            7 : '1440p',
            8 : '1080pSuperview',
            9 : '1080p',
            10 : '960p',
            11 : '720pSuperview',
            12 : '720p',
            13 : 'WVGA'}
        },
        'shutter':{
        'cmd' : 'command/shutter?p=',
        'translate' : {
            1:'on',
            0:'off'}
        },
        'deleteall':{ # run as command('deleteall', '').
        #takes an empty string as a parameter
        'cmd' : 'command/storage/delete/all',
        'translate' : {
            '':'1'}
        }
    }

    def __init__(
            self, ip='10.5.5.9', password='password', log_level=logging.INFO):
        self._ip = ip
        self._password = password

        # setup log
        log_format = '%(asctime)s   %(message)s'
        logging.basicConfig(format=log_format, level=log_level)

    def password(self, password=None):
        if password is None:
            return self._password
        else:
            self._password = password

    def originalStatus(self):
        status = {
            # summary = 'notfound', 'sleeping', 'on', or 'recording'
            'summary': 'notfound',
            'raw': {}
        }
        camActive = True

        http = urllib3.PoolManager()

        # loop through different status URLs
        for cmd in self.originalStatusMatrix:

            # stop sending requests if a previous request failed
            if camActive:
                url = self._originalStatusURL(cmd)

                # attempt to contact the camera
                r = http.request('GET', url)
                response = r.data.encode('hex')
                status['raw'][cmd] = response  # save raw response

                # loop through different parts we know how to translate
                for item in self.originalStatusMatrix[cmd]:
                    args = self.originalStatusMatrix[cmd][item]
                    if 'a' in args and 'b' in args:
                        part = response[args['a']:args['b']]
                    else:
                        part = response

                    # translate the response value if we know how
                    if 'translate' in args:
                        status[item] = self._translate(
                            args['translate'], part)
                    else:
                        status[item] = part


        # build summary
        if 'record' in status and status['record'] == 'on':
            status['summary'] = 'recording'
        elif 'power' in status and status['power'] == 'on':
            status['summary'] = 'on'
        elif 'power' in status and status['power'] == 'sleeping':
            status['summary'] = 'sleeping'

        #logging.info('GoProHero.status() - result {}'.format(status))
        return status

    def status(self):
        timeout = 2.0

        status = {
            # summary = 'notfound', 'sleeping', 'on', or 'recording'
            'summary': 'notfound',
            'raw': {},
            'state':{}
        }
        camActive = True

        #get and store the 31 bytes of status
        statusUrl = self._statusURL()

        http = urllib3.PoolManager()

        r = http.request('GET', statusUrl)

        if r.status == 200:
            cameraState = list(r.data.encode('hex'))
            cameraStateBytes = []

            for index in range(len(cameraState)):
                if index % 2 == 0:
                    cameraStateBytes.append(cameraState[index] + "" + cameraState[index+1])
                    index += 1

            status["raw"] = cameraStateBytes

            for item in self.statusMatrix:
                 if (self.statusMatrix[int(item)] != {}): #some bytes are unknown
                    #item
                    singleStateDictionary = self.statusMatrix[int(item)]
                    for key in singleStateDictionary:
                        try:
                            if (singleStateDictionary[key] != 'variable'):
                                status["state"][key] = singleStateDictionary[key][int(status["raw"][item])]
                            else:
                                status["state"][key] = status["raw"][item]
                        except KeyError as e:
                            print str(e) + " not defined in " + key

        return status

        #status['raw'] = response  # save raw response

        # loop through different parts we know how to translate

        #     print status["raw"][int(item)]
        #     args = self.statusMatrix[cmd][item]
        #     if 'a' in args and 'b' in args:
        #         part = response[args['a']:args['b']]
        #     else:
        #         part = response
        #
        #     # translate the response value if we know how
        #     if 'translate' in args:
        #         status[item] = self._translate(
        #             args['translate'], part)
        #     else:
        #         status[item] = part

        # # build summary
        # if 'record' in status and status['record'] == 'on':
        #     status['summary'] = 'recording'
        # elif 'power' in status and status['power'] == 'on':
        #     status['summary'] = 'on'
        # elif 'power' in status and status['power'] == 'sleeping':
        #     status['summary'] = 'sleeping'
        #
        # logging.info('GoProHero.status() - result {}'.format(status))

    def image(self):
        try:
            # use OpenCV to capture a frame and store it in a numpy array
            stream = cv2.VideoCapture(self._previewURL())
            success, numpyImage = stream.read()

            if success:
                # use Image to save the image to a file, but actually save it
                # to a string
                image = Image.fromarray(numpyImage)
                output = StringIO.StringIO()
                image.save(output, format='PNG')
                str = output.getvalue()
                output.close()

                logging.info('GoProHero.image() - success!')
                return 'data:image/png;base64,'+base64.b64encode(str)
        except NameError:
            logging.warning('{}{} - OpenCV not installed{}'.format(
                Fore.YELLOW, 'GoProHero.image()', Fore.RESET))
        except IOError as e:
            logging.warning('{}{} - Pillow prereqs not installed: {}{}'.format(
                Fore.YELLOW, 'GoProHero.image()', e, Fore.RESET))

        # catchall return statement
        return False

    def command(self, command, value=None):
        http = urllib3.PoolManager()

        commandUrl = self._commandURL(command, value)

        r = http.request('GET', commandUrl)
        if (r.status == 200):
            if(r.data != '{}\n'): #this is an empty response (means success)
                print r.data
        else:
            print commandUrl + " didn't work"

        # func_str = 'GoProHero.command({}, {})'.format(command, value)
        #
        # if command in self.commandMaxtrix:
        #     args = self.commandMaxtrix[command]
        #     # accept both None and '' for commands without a value
        #     if value == '':
        #         value = None
        #     # for commands with values, translate the value
        #     if value is not None and value in args['translate']:
        #         value = args['translate'][value]
        #     # build the final url
        #     url = self._commandURL(args['cmd'], value)
        #
        #     # attempt to contact the camera
        #     try:
        #         urlopen(url, timeout=self.timeout).read()
        #         logging.info('{} - http success!'.format(func_str))
        #         return True
        #     except (HTTPError, URLError, socket.timeout) as e:
        #         logging.warning('{}{} - error opening {}: {}{}'.format(
        #             Fore.YELLOW, func_str, url, e, Fore.RESET))

        # catchall return statement
        return False

    def test(self, url, toHex=True):
        try:
            url = 'http://{}/{}'.format(self._ip, url)

            print(url)
            response = urlopen(
                url, timeout=self.timeout).read()

            if toHex:
                response = response.encode('hex')

            print(response)
        except (HTTPError, URLError, socket.timeout) as e:
            print(e)

    def _translate(self, config, value):
        if isinstance(config, dict):
            # use a lookup dictionary
            if value in config:
                return config[value]
            else:
                return 'translate error: {} not found'.format(value)
        else:
            # use an internal function
            if hasattr(self, config):
                return getattr(self, config)(value)
            else:
                return 'translate error: {} not a function'.format(value)
