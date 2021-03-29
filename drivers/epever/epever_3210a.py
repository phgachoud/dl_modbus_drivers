#!/usr/bin/env python3
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#       DESCRIPTION: 
#
#       CALL SAMPLE:
#	
#	
#		DOCS
#			see ../../docs directory	
#	
#	REQUIRE
#
#       CALL PARAMETERS:
#               1) 
#
#       @author: Philippe Gachoud
#       @creation: 20210326
#       @last modification:
#       @version: 1.0
#       @URL: $URL
#
#		LICENCE: MIT
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# INCLUDES
try:
	import sys
	import os.path
	sys.path.append(os.path.join(os.path.dirname(__file__), '../../lib'))
	import os, errno
	import logging # http://www.onlamp.com/pub/a/python/2005/06/02/logging.html
	from logging import handlers
	import argparse
	from pymodbus.pdu import ModbusRequest
	from pymodbus.client.sync import ModbusSerialClient as ModbusSerialClient #initialize a serial RTU client instance https://github.com/riptideio/pymodbus/blob/master/pymodbus/client/sync.py
	#from pymodbus.client.sync import ModbusTcpClient as ModbusTcpClient # FOR TCP
	from pymodbus.transaction import ModbusRtuFramer
	#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pysunspec'))
	from datetime import datetime, date, time, timedelta
#	import jsonpickle # pip install jsonpickle
#	import json
	from dl_logger import DlLogger
	from collections import OrderedDict
	#from sit_constants import SitConstants
	#from sit_date_time import SitDateTime
except ImportError as l_err:
	print("ImportError: {0}".format(l_err))
	raise l_err

#filename: my_class.py
class Epever3210a(object):

# CONSTANTS


# VARIABLES
	_logger = None
	_console_handler = None
	_file_handler = None

	_modbus_client = None


# SETTERS AND GETTERS

	@property
	def logger(self):
		return self._logger

	@logger.setter
	def logger(self, v):
		self._logger = v

# FUNCTIONS DEFINITION 

	def __init__(self):
		"""
			Initialize
		"""
		try:
			self.init_arg_parse()
			#*** Logger
			self._logger = DlLogger().new_logger(__name__)
		except OSError as l_e:
			self._logger.warning("init-> OSError, probably rollingfileAppender:{}".format(l_e))
			if e.errno != errno.ENOENT:
				raise l_e
		except Exception as l_e:
			self._logger.error('Error in init: {}'.format(l_e))
			raise l_e
			#exit(1)

# SCRIPT ARGUMENTS

	def init_arg_parse(self):
		"""
			Parsing arguments
		"""
		self._parser = argparse.ArgumentParser(description='Actions with Epever3210a through USB dongle')
		self._add_arguments()
		args = self._parser.parse_args()
		self._args = args

	def _add_arguments(self):
		"""
		Add arguments to parser (called by init_arg_parse())
		"""
		self._parser.add_argument('-v', '--verbose', help='increase output verbosity', action="store_true")
		self._parser.add_argument('-u', '--update_leds_status', help='Updates led status according to spec', action="store_true")
		self._parser.add_argument('-t', '--test', help='Runs test method', action="store_true")

		#self._parser.add_argument('-u', '--base_url', help='NOT_IMPLEMENTED:Gives the base URL for requests actions', nargs='?', default=self.DEFAULT_BASE_URL)
		l_required_named = self._parser.add_argument_group('required named arguments')
#		l_required_named.add_argument('-i', '--host_ip', help='Host IP', nargs='?', required=True)
#		l_required_named.add_argument('-u', '--slave_address', help='Slave address of modbus device', nargs='?', required=True)
#		l_required_named.add_argument('-m', '--host_mac', help='Host MAC', nargs='?', required=True)
#		l_required_named.add_argument('-l', '--longitude', help='Longitude coordinate (beware timezone is set to Chile)', nargs='?', required=True)
#		l_required_named.add_argument('-a', '--lattitude', help='Lattitude coordinate (beware timezone is set to Chile)', nargs='?', required=True)
#		l_required_named.add_argument('-d', '--device_type', help='Device Type:' + ('|'.join(str(l) for l in self.DEVICE_TYPES_ARRAY)), nargs='?', required=True)

	def execute_corresponding_args( self ):
		"""
			Parsing arguments and calling corresponding functions
		"""
		if self._args.verbose:
			self._logger.setLevel(logging.DEBUG)
		else:
			self._logger.setLevel(logging.INFO)
		if self._args.test:
			self.test()
		#if self._args.store_values:

	
# TEST

	def test(self):
		"""
			Test function
		"""
		try:
			self._logger.info("################# BEGIN #################")
			l_serial_port = '/dev/ttyUSB0'
			self._modbus_client = ModbusSerialClient(method="rtu", port=l_serial_port, timeout=4, stopbits=1, bytesize=8, baudrate=115200)
			self._modbus_client.connect()

			l_od = OrderedDict()

			l_registers_array = self._modbus_client.read_input_registers(0x3100, 4, unit=1)
			l_od['solar_voltage,V'] = float(l_registers_array.registers[0] / 100.0)
			l_od['solar_current,A'] = float(l_registers_array.registers[1] / 100.0)
			l_od['input_power_l,W'] = float(l_registers_array.registers[2] / 100.0)
			l_od['input_power_h,W'] = float(l_registers_array.registers[3] / 100.0)

			l_registers_array = self._modbus_client.read_input_registers(0x310C, 4, unit=1)
			l_od['load_voltage,V'] = float(l_registers_array.registers[0] / 100.0)
			l_od['load_current,A'] = float(l_registers_array.registers[1] / 100.0)
			l_od['load_power_l,W'] = float(l_registers_array.registers[2] / 100.0)
			l_od['load_power_h,W'] = float(l_registers_array.registers[3] / 100.0)

			l_registers_array = self._modbus_client.read_input_registers(0x3302, 8, unit=1)
			l_od['max_battery_voltage_today,V'] = float(l_registers_array.registers[0] / 100.0)
			l_od['min_battery_voltage_today,A'] = float(l_registers_array.registers[1] / 100.0)
			l_od['tot_energy_today L,kWh'] = float(l_registers_array.registers[2] / 100.0)
			l_od['tot_energy_today H,kWh'] = float(l_registers_array.registers[3] / 100.0)
			l_od['tot_energy_month L,kWh'] = float(l_registers_array.registers[4] / 100.0)
			l_od['tot_energy_month H,kWh'] = float(l_registers_array.registers[5] / 100.0)

			l_registers_array = self._modbus_client.read_input_registers(0x330A, 6, unit=1)
			l_od['total_consumed_energy L,kWh'] = float(l_registers_array.registers[0] / 100.0)
			l_od['total_consumed_energy H,kWh'] = float(l_registers_array.registers[1] / 100.0)
			l_od['generated_energy_today L,kWh'] = float(l_registers_array.registers[2] / 100.0)
			l_od['generated_energy_today H,kWh'] = float(l_registers_array.registers[3] / 100.0)
			l_od['generated_energy_this_month L,kWh'] = float(l_registers_array.registers[4] / 100.0)
			l_od['generated_energy_this_month H,kWh'] = float(l_registers_array.registers[5] / 100.0)

#			l_registers_array = self._modbus_client.read_input_registers(0x9013, 3, unit=1) #P.15 of doc
#			l_od['real_time_clock,YMDHMS'] = float(l_registers_array.registers[0] / 100.0)



			for l_key, l_val in l_od.items():
				l_tmp_array = l_key.split(',')
				l_label = l_tmp_array[0]
				l_unit = l_tmp_array[1]
				self._logger.info('{}: {} {}'.format(l_label, l_val, l_unit))

			self._modbus_client.close()
			self._logger.info("################# END #################")
			
		except Exception as l_e:
			self._logger.exception("Exception occured:  {}".format(l_e))
			print('Error: {}'.format(l_e))
			self._logger.error('Error: {}'.format(l_e))
			sys.exit(1)

#################### END CLASS ######################

def main():
	"""
	Main method
	"""
	#logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")
	logger = logging.getLogger(__name__)

	try:
		l_obj = Epever3210a()
		l_obj.execute_corresponding_args()
#		l_id.test()
	except KeyboardInterrupt:
		logger.exception("Keyboard interruption")
	except Exception as l_e:
		logger.exception("Exception occured:{}".format(l_e))
		raise l_e


#Call main if this script is executed
if __name__ == '__main__':
    main()
