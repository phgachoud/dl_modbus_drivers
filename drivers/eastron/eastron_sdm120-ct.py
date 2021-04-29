#!/usr/bin/env python3
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#		DESCRIPTION: 
#			Python modbus driver to get and store Eastron SDM120CT meter data into a CSV file
#				
#		CALL SAMPLE:
#			see this_file.py -h				
#	
#		DOCS
#			see ../../docs directory	
#	
#		REQUIRE
#			pip3 install pymodbus
#
#		CALL PARAMETERS:
#				1) 
#
#		@author: Philippe Gachoud
#		@creation: 20210426
#		@last modification:
#		@version: 1.0
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
	from datetime import datetime, date, time, timedelta
	from dl_modbus_item import DlModbusItem
	from dl_logger import DlLogger
	from dl_bytes_decoder import DlBytesDecoder
	from collections import OrderedDict
	from pymodbus.constants import Endian
	from pymodbus.payload import BinaryPayloadDecoder
	from pymodbus.payload import BinaryPayloadBuilder
	import csv
except ImportError as l_err:
	print("ImportError: {0}".format(l_err))
	raise l_err

#filename: my_class.py
class EastronSdm120Ct(object):

# CONSTANTS


# VARIABLES
	_logger = None
	_console_handler = None
	_file_handler = None
	_csv_file_dir = '/var/dl/'
	_slave_address = 1
	_serial_port = '/dev/ttyUSB0'
	_baudrate = 2400
	_dl_bytes_decoder = DlBytesDecoder()


	_modbus_client = None

	_modbus_items = []


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
		self._parser = argparse.ArgumentParser(description='Actions with EastronSdm120Ct through USB dongle')
		self._add_arguments()
		args = self._parser.parse_args()
		self._args = args

	def _add_arguments(self):
		"""
		Add arguments to parser (called by init_arg_parse())
		"""
		self._parser.add_argument('-v', '--verbose', help='increase output verbosity', action="store_true")
		self._parser.add_argument('-d', '--display_results', help='Display results as logger.info', action="store_true")
		self._parser.add_argument('-s', '--store_csv', help='stores output to CSV', action="store_true")
		self._parser.add_argument('-t', '--test', help='Runs test method', action="store_true")

	def execute_corresponding_args( self ):
		"""
			Parsing arguments and calling corresponding functions
		"""
		try:
			if self._args.verbose:
				self._logger.setLevel(logging.DEBUG)
			else:
				self._logger.setLevel(logging.INFO)

			self._modbus_client = ModbusSerialClient(method="rtu", port=self._serial_port, parity='N', timeout=3, stopbits=1, bytesize=8, baudrate=self._baudrate)
			self._modbus_client.connect()
			if self._args.test:
				self.test()

			self.read_items()
			if self._args.display_results:
				self.display_items()

			if self._args.store_csv:
				self.store_to_csv()
		except Exception as l_e:
			self._logger.error('Error in execute_corresponding_args: {}'.format(l_e))
			self._modbus_client.close()
			raise l_e

	def extend_items(self, a_dl_modbus_item):
		"""
		Adds given item to self._modbus_items
		"""
		self._modbus_items.append(a_dl_modbus_item)


	def read_items(self):
		"""
			Reads all items
		"""
		self.extend_items(DlModbusItem(0, 'Voltage', 'V', 2, 'V', 0))
		self.extend_items(DlModbusItem(6, 'Current', 'A', 2, 'A', 0))
		self.extend_items(DlModbusItem(12, 'Active Power', 'P', 2, 'W', 0))
		self.extend_items(DlModbusItem(18, 'Apparent Power', 'Q', 2, 'VA', 0))
		self.extend_items(DlModbusItem(24, 'Reactive Power', 'S', 2, 'VAr', 0))
		self.extend_items(DlModbusItem(30, 'Power Factor', 'PF', 2, '', 0))
		self.extend_items(DlModbusItem(36, 'Phase angle', 'PA', 2, 'Deg', 0))
		self.extend_items(DlModbusItem(70, 'Frequency', 'F', 2, 'Hz', 0))
		self.extend_items(DlModbusItem(72, 'Import active energy', 'PImp', 2, 'kWh', 0))
		self.extend_items(DlModbusItem(74, 'Export active energy', 'PExp', 2, 'kWh', 0))
		self.extend_items(DlModbusItem(76, 'Import reactive energy', 'QImp', 2, 'kVArh', 0))
		self.extend_items(DlModbusItem(78, 'Export reactive energy', 'QExp', 2, 'kVArh', 0))
		self.extend_items(DlModbusItem(342, 'Total Active Energy', 'PTot', 2, 'kWh', 0))
		self.extend_items(DlModbusItem(344, 'Total Reactive Energy', 'QTot', 2, 'kVArh', 0))

		self.read_modbus_items()

	def read_modbus_items(self):
		for l_item in self._modbus_items:
			self._logger.debug('--> reading register:{} registers_count:{} slave:{}'.format(l_item._address, l_item._registers_count, self._slave_address))
			try:
				l_registers_array = self._modbus_client.read_input_registers(l_item._address, l_item._registers_count, unit=self._slave_address)
				#self._logger.debug('-- register result:{}'.format(l_registers_array))
				l_val = self.read_float_32(l_item._address, l_item._registers_count)
				l_val = round(l_val, 2)

				l_item._item = l_val
			except Exception as l_e:
				self._logger.warning('Unable to get a valid answer from register "{}" index:{}/hex({}), registers_count:{}'.format(l_item._description, l_item._address, hex(l_item._address), l_item._registers_count))
				raise l_e


	def display_items(self):
		"""
		Displays information with logger on self._modbus_items
		"""
		for l_item in self._modbus_items:
			self._logger.info(l_item.out())

	def get_mac(self):
		from uuid import getnode as get_mac
		mac = get_mac()
		l_res = '-'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
		l_res = l_res.lower()
		
		self._logger.warning('mac:{}-'.format(l_res))
		return l_res

	def csv_file_path(self):
		"""
		returns a complete file path for csv exporting
		creates directory if not exists
		"""
		l_res = os.path.join(self._csv_file_dir, str(datetime.today().year), '{:02d}'.format(datetime.today().month))
		if not os.path.exists(l_res):
			os.makedirs(l_res)
		l_fname = datetime.today().strftime('%Y%m%d') + '_' + self.get_mac() + '_' + self.__class__.__name__ + '.csv'
		l_res = os.path.join(l_res, l_fname)
		return l_res

	def _header_rows(self):
		l_res = []
		l_res.append(['#Device', self.__class__.__name__])
		l_res.append(['#Mac', self.get_mac()])
		return l_res

	def store_to_csv(self):
		try:
			l_f_name = self.csv_file_path()
			l_file_exists = os.path.isfile(l_f_name)
			self._logger.info("store_to_csv->Writting into file {} exists:{}".format(l_f_name, l_file_exists))
			with open(l_f_name, mode='a+') as l_csv_file:
				l_csv_writter = csv.writer(l_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				if not l_file_exists:
					#Header comments
					for l_header_row in self._header_rows():
						self._logger.info("store_values_into_csv->writting header:{}".format(l_header_row))
						l_csv_writter.writerow(l_header_row)
						self._logger.info("store_to_csv->Writting METADATA row: %s" % (';'.join(str(l) for l in l_header_row)))
					#Headers
					l_fields_abbr_row = []
					l_fields_abbr_row.append('Timestamp')
					for l_dl_modbus_item in self._modbus_items:
						l_fields_abbr_row.append(l_dl_modbus_item._abbreviation)
					l_csv_writter.writerow(l_fields_abbr_row)
					self._logger.info("store_to_csv->Writting Headers row: %s" % (';'.join(str(l) for l in l_fields_abbr_row)))
				# Metadata and registers
				l_values_dict = []
				l_values_dict.append(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
				for l_dl_modbus_item in self._modbus_items:
					l_values_dict.append(l_dl_modbus_item._item)

				#Registers no metadata
				self._logger.info("store_to_csv->Writting row: %s" % ('|'.join(str(l) for l in l_values_dict)))
				l_csv_writter.writerow(l_values_dict)
		except Exception as l_e:
			self._logger.error('store_values_into_csv->Error: %s' % l_e)
			raise l_e



	def read_float_32(self, start_address, registers_count):
		l_registers_array = self._modbus_client.read_input_registers(start_address, registers_count, unit=self._slave_address)
		decoder = BinaryPayloadDecoder.fromRegisters(l_registers_array.registers, Endian.Big, wordorder=Endian.Big)
		return decoder.decode_32bit_float()
		
# TEST

	def test(self):
		"""
			Test function
		"""
		try:
			self._logger.info("################# BEGIN #################")

			l_od = OrderedDict()

			l_registers_array = self._modbus_client.read_input_registers(0x0, 2, unit=1)
			l_od['Voltage,V'] = self.read_float_32(0, 2)
			l_od['Current,A'] = self.read_float_32(6, 2)
			l_od['Active Power,W'] = self.read_float_32(12, 2)


			for l_key, l_val in l_od.items():
				l_tmp_array = l_key.split(',')
				l_label = l_tmp_array[0]
				l_unit = l_tmp_array[1]
				self._logger.info('{}: {} {}'.format(l_label, l_val, l_unit))

			self._logger.info("################# END #################")
			
		except Exception as l_e:
			self._logger.exception("Exception occured:	{}".format(l_e))
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
		l_obj = EastronSdm120Ct()
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
