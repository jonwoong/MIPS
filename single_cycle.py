SC_CONTROL_SIGNALS = {
	'reg_dst' : '0',
	'ALU_src' : '0',
	'mem_to_reg' : '0',
	'reg_write' : '0',
	'mem_read' : '0',
	'mem_write' : '0',
	'branch' : '0',
	'ALU_op' : '00',
	'jump' : '0',
	'ui_to_reg': '0'
}

SC_DATA_MEMORY = {
	'address' : '0',
	'write_data' : '0',
	'read_data' : '0'
}

SC_REGISTER_FILE = {
	'read_reg_1' : '0',
	'read_reg_2' : '0',
	'write_reg' : '0',
	'write_data' : '0',
	'read_data_1' : '0',
	'read_data_2' : '0'
}

SC_ALU_UNIT = {
	'zero': '0',
	'result': '0'
}

def set_register_file(rr1,rr2,wr,rd1,rd2,wd=0):
	REGISTER_FILE['read_reg_1'] = rr1
	REGISTER_FILE['read_reg_2'] = rr2
	REGISTER_FILE['write_reg'] = wr
	REGISTER_FILE['write_data'] = wd
	REGISTER_FILE['read_data_1'] = rd1
	REGISTER_FILE['read_data_2'] = rd2
	return

def set_data_memory(addr,wd,rd):
	DATA_MEMORY['address'] = addr
	DATA_MEMORY['write_data'] = wd
	DATA_MEMORY['read_data'] = rd
	return

def initialize_registers():
	key_list = [to_binary('reg',i) for i in range(32)]
	R = R.fromkeys(key_list,to_binary('int',0))
	return 

def set_register(number,value):
	R[to_binary('reg',number)] = to_binary('int',value)
	return

def set_control_signals(regdst=0,alusrc=0,memtoreg=0,regwrite=0,memread=0,memwrite=0,br=0,aluop=0,j=0,uitoreg=0):
	SC_CONTROL_SIGNALS['reg_dst'] = regdst
	SC_CONTROL_SIGNALS['ALU_src'] = alusrc
	SC_CONTROL_SIGNALS['mem_to_reg'] = memtoreg
	SC_CONTROL_SIGNALS['reg_write'] = regwrite
	SC_CONTROL_SIGNALS['mem_read'] = memread
	SC_CONTROL_SIGNALS['mem_write'] = memwrite
	SC_CONTROL_SIGNALS['branch'] = br
	SC_CONTROL_SIGNALS['ALU_op'] = aluop
	SC_CONTROL_SIGNALS['jump'] = j
	SC_CONTROL_SIGNALS['ui_to_reg'] = uitoreg
	return

def control(op):
	if (op=='000000'): # R-type
		set_control_signals('1','0','0','1','0','0','0','10','0','0')
	elif (op=='100011'): # LW
		set_control_signals('0','1','1','1','1','0','0','00','0','0')
	elif (op=='101011'): # SW
		set_control_signals('X','1','X','0','0','1','0','00','0','0')
	elif (op=='000100'): # beq
		set_control_signals('X','0','X','0','0','0','1','01','0','0')
	elif (op=='000010'): # jump
		set_control_signals('X','X','X','0','X','0','X','XX','1','0')
	elif (op=='001111'): # lui
		set_control_signals('0','X','X','1','X','0','0','XX','0','1')

def reg_dst_MUX(rt,rd,signal):
	if (signal=='0'):
		return rt
	else:
		return rd

def ALU_src_MUX(rf_rd2,se_imm,signal):
	if (signal=='0'):
		return rf_rd2
	else:
		return se_imm

def branch_MUX(inc_PC,se_imm_sl2,signal):
	if (signal=='0'):
		return inc_PC
	else:
		return se_imm_sl2

def branch_AND(signal,zero):
	if (signal=='1' and zero=='1'):
		return '1'
	else:
		return '0'

def mem_to_reg_MUX(alu_result,dm_rd,signal):
	if (signal=='1'):
		return dm_rd
	else:
		return alu_result

def data_memory_logic(addr,wd,memw,memr):
	DATA_MEMORY['address'] = addr
	DATA_MEMORY['write_data'] = wd
	if (memr=='1'):
		DATA_MEMORY['read_data'] = MEM[addr]
		return DATA_MEMORY['read_data']
	elif (memw=='1'):
		MEM[addr] = DATA_MEMORY['write_data']
	return DATA_MEMORY['read_data']

def update_register_file(regw,wd):
	REGISTER_FILE['write_data'] = wd
	if (regw=='1'):
		R[REGISTER_FILE['write_reg']] = REGISTER_FILE['write_data']
	return

def jump_MUX(branch_mux,jump_addr,signal):
	if (signal=='1'):
		return jump_addr
	else:
		return branch_mux

def calculate_jump_addr(target,inc_PC):
	return inc_PC[0:4] + shift_left(target,2)

def ui_to_reg_MUX(mem_to_reg_MUX,imm,signal):
	if (signal=='1'):
		return shift_left(sign_extend(imm,16),16)
	else:
		return mem_to_reg_MUX

