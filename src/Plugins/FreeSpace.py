#######################################################################
#
#    Push Service for Enigma-2
#    Coded by betonme (c) 2012 <glaserfrank(at)gmail.com>
#    Support: http://www.i-have-a-dreambox.com/wbb2/thread.php?threadid=167779
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#######################################################################

# Config
from Components.config import ConfigYesNo, ConfigText, ConfigNumber, NoSave

# Plugin internal
from Plugins.Extensions.PushService.__init__ import _
from Plugins.Extensions.PushService.PluginBase import PluginBase

# Plugin specific
import os


SUBJECT = _("Free space warning")
BODY    = _("Free disk space limit has been reached:\n") \
				+ _("Path:  %s\n") \
				+ _("Limit: %d GB\n") \
				+ _("Left:  %s")


class FreeSpace(PluginBase):
	
	ForceSingleInstance = False
	
	def __init__(self):
		# Is called on instance creation
		PluginBase.__init__(self)
		
		# Default configuration
		self.setOption( 'wakehdd',  NoSave(ConfigYesNo(  default = False )),                                  _("Allow HDD wake up") )
		self.setOption( 'path',     NoSave(ConfigText(   default = "/media/hdd/movie", fixed_size = False )), _("Where to check free space") )
		self.setOption( 'limit',    NoSave(ConfigNumber( default = 100 )),                                    _("Free space limit in GB") )
	
	def run(self):
		# Return Header, Body, Attachment
		# If empty or none is returned, nothing will be sent
		path = self.getValue('path')
		limit = self.getValue('limit')
		
		if not self.getValue('wakehdd'):
			def mountpoint(path):
				path = os.path.realpath(path)
				if os.path.ismount(path) or len(path)==0: return path
				return mountpoint(os.path.dirname(path))
			
			# User specified to avoid HDD wakeup if it is sleeping
			from Components.Harddisk import harddiskmanager
			p = harddiskmanager.getPartitionbyMountpoint( mountpoint(path) )
			if p is not None and p.uuid is not None:
				dev = harddiskmanager.getDeviceNamebyUUID(p.uuid)
				if dev is not None:
					hdd = harddiskmanager.getHDD(dev)
					if hdd is not None:
						if hdd.isSleeping():
							# Don't wake up HDD
							print _("[FreeSpace] HDD is idle: ") + str(path)
							return
						#TODO TEST
						else:
							print _("[FreeSpace] TEST HDD is not idle: ") + str(path)
		
		# Check free space on path
		if os.path.exists( path ):
			stat = os.statvfs( path )
			free = ( stat.f_bavail if stat.f_bavail!=0 else stat.f_bfree ) * stat.f_bsize / 1024 / 1024 # MB
			if limit > (free/1024): #GB
				if free >= 10*1024:	#MB
					free = "%d GB" %(free/1024)
				else:
					free = "%d MB" %(free)
				# Not enough free space
				return SUBJECT, BODY % (path, limit, free)
			else:
				# There is enough free space
				return None
