def to_binary(field,value):
	if (field=='reg'):
		return '{0:{fill}5b}'.format(value,fill='0')
	elif (field=='imm'):
		return '{0:{fill}16b}'.format(value,fill='0')
	elif (field=='offset'):
		return '{0:{fill}16b}'.format(value,fill='0')
	elif (field=='int'):
		return '{0:{fill}32b}'.format(value,fill='0')
	elif (field=='target'):
		return '{0:{fill}26b}'.format(value,fill='0')

def binary_add(a,b):
	return to_binary('int',int(a,2) + int(b,2))

########## DATA STRUCTURES ##########
CONTROL_SIGNAL_NAMES = [
	'PC_write',
	'I_or_D',
	'mem_read',
	'mem_write',
	'ir_write',
	'reg_dst',
	'reg_write',
	'ALU_src_A',
	'ALU_src_B',
	'ALU_op',
	'mem_to_reg',
	'PC_src',
	'PC_write_cond']
CONTROL_SIGNALS = dict.fromkeys(CONTROL_SIGNAL_NAMES)

MEMORY_FIELDS = ['address','mem_data','write_data']
MEMORY = dict.fromkeys(MEMORY_FIELDS)

INSTRUCTION_REGISTER_FIELDS = ['op','rs','rt','imm']
INSTRUCTION_REGISTER = dict.fromkeys(INSTRUCTION_REGISTER_FIELDS)

REGISTER_FILE_FIELDS = ['read_reg_1','read_reg_2','write_reg','write_data','read_data_1','read_data_2']
REGISTER_FILE = dict.fromkeys(REGISTER_FILE_FIELDS)

ALU_FIELDS = ['zero','result']
ALU = dict.fromkeys(ALU_FIELDS)

PC = ''
REGISTER_KEYS = [to_binary('reg',i) for i in range(32)]
R = dict.fromkeys(REGISTER_KEYS)
DATA_MEMORY = {} # actual RAM
MEM_DATA_REG = ''
REG_A = ''
REG_B = ''
ALU_OUT = ''
CURRENT_INSN = ''

######### FUNCTIONS ##########
def add_word_to_memory(addr,word):
	DATA_MEMORY[addr] = word
	return

def ALU_control(op,funct):
	if (op==0): # LW/SW
		return '0010'
	elif (op==1): # BEQ
		return '0110'
	elif (op==2): # R-type
		if (funct=='100000'): # ADD
			return '0010'
		elif (funct=='100010'): # SUB
			return '0110'
		elif (funct=='100100'): # AND
			return '0000'
		elif (funct=='100101'): # OR
			return '0001'
		elif (funct=='101010'): # SLT
			return '0111'

def ALU_execute(op,a,b):
	if (op=='0000'): # AND
		return to_binary((int(a,2)&int(b,2)),32)
	elif (op=='0001'): # OR 
		return to_binary((int(a,2)|int(b,2)),32) 
	elif (op=='0010'): # ADD
		return binary_add(a,b) 
	elif (op=='0110'): # SUB
		return to_binary((int(a,2)-int(b,2)),32)
	elif (op=='0111'): # SLT
		if (a<b):
			ALU['zero'] = 1
		else:
			ALU['zero'] = 0
		return to_binary((int(a,2)-int(b,2)),32)
	elif (op=='1100'): # NOR
		return to_binary(not(int(a,2)|int(b,2)),32)

def set_register(number,value):
	R[to_binary('reg',number)] = to_binary('int',value)
	return

def sign_extend(value,amt):
	extension = '0'* amt
	return extension + value

def shift_left(value,amt):
	extension = '0' * amt
	value = value[amt::]
	return value + extension

def generate_fetch_signals():
	signal_values = [1,0,1,0,1,0,0,0,1,0,0,0,0]
	CONTROL_SIGNALS.update(dict(zip(CONTROL_SIGNAL_NAMES,signal_values)))
	return

def generate_decode_signals():
	signal_values = [0,0,0,0,0,0,0,0,3,0,0,0,0]
	CONTROL_SIGNALS.update(dict(zip(CONTROL_SIGNAL_NAMES,signal_values)))
	return

def generate_execute_signals():
	global CURRENT_INSN
	insn_name = CURRENT_INSN[0]
	insn_type = CURRENT_INSN[1]
	signal_values = []
	if (insn_type=='R'):
		signal_values = [0,0,0,0,0,0,0,1,0,2,0,0,0]
	elif (insn_name=='lw' or insn_name=='sw'):
		signal_values = [0,0,0,0,0,0,0,1,2,0,0,0,0]
	elif (insn_name=='beq'):
		signal_values = [0,0,0,0,0,0,0,1,0,1,0,1,1]
	elif (insn_type=='J'):
		signal_values = [1,0,0,0,0,0,0,0,0,0,0,2,0]
	CONTROL_SIGNALS.update(dict(zip(CONTROL_SIGNAL_NAMES,signal_values)))
	return

def generate_memory_signals():
	global CURRENT_INSN
	insn_name = CURRENT_INSN[0]
	insn_type = CURRENT_INSN[1]
	signal_values = []
	if (insn_type=='R'):
		signal_values = [0,0,0,0,0,1,1,0,0,0,0,0,0]
	elif (insn_name=='lw'):
		signal_values = [0,1,1,0,0,0,0,0,0,0,0,0,0]
	elif (insn_name=='sw'):
		signal_values = [0,1,0,1,0,0,0,0,0,0,0,0,0]
	elif (insn_type=='J'):
		signal_values = [0,0,0,0,0,0,0,0,0,0,0,0,0]
	CONTROL_SIGNALS.update(dict(zip(CONTROL_SIGNAL_NAMES,signal_values)))
	return

def generate_write_back_signals():
	global CURRENT_INSN
	insn_name = CURRENT_INSN[0]
	signal_values = []
	if (insn_name=='lw'):
		signal_values = [0,0,0,0,0,0,1,0,0,0,1,0,0]
		CONTROL_SIGNALS.update(dict(zip(CONTROL_SIGNAL_NAMES,signal_values)))
	return

def I_or_D_MUX(PC,ALU_out):
	if (CONTROL_SIGNALS['I_or_D']):
		return ALU_out
	else:
		return PC

def reg_dst_MUX(rt,rd):
	if (CONTROL_SIGNALS['reg_dst']):
		return rd
	else:
		return rt

def ALU_src_A_MUX(PC,reg_A):
	if (CONTROL_SIGNALS['ALU_src_A']):
		return reg_A
	else:
		return PC

def ALU_src_B_MUX(reg_B,se_imm,se_imm_ls):
	if (CONTROL_SIGNALS['ALU_src_B']==0):
		return reg_B
	elif (CONTROL_SIGNALS['ALU_src_B']==1):
		return to_binary('int',4)
	elif (CONTROL_SIGNALS['ALU_src_B']==2):
		return se_imm
	else:
		return se_imm_ls

def PC_src_MUX(inc_PC,ALU_out,j_target):
	if (CONTROL_SIGNALS['PC_src']==0):
		return inc_PC
	elif (CONTROL_SIGNALS['PC_src']==1):
		return ALU_out
	else:
		return j_target

def mem_to_reg_MUX(ALU_out,mem_data_reg):
	if (CONTROL_SIGNALS['mem_to_reg']):
		return mem_data_reg
	else:
		return ALU_out

def update_MEMORY():
	global CURRENT_INSN
	global REG_B
	global ALU_OUT
	global MEM_DATA_REG
	MEMORY['address'] = I_or_D_MUX(PC,ALU_OUT)
	MEMORY['write_data'] = REG_B
	if (CONTROL_SIGNALS['mem_read']):
		CURRENT_INSN = DATA_MEMORY[MEMORY['address']]
		MEMORY['mem_data'] = CURRENT_INSN[2]
	elif (CONTROL_SIGNALS['mem_write']):
		DATA_MEMORY[MEMORY['address']] = MEMORY['write_data']
	MEM_DATA_REG = MEMORY['mem_data']
	return

def update_INSTRUCTION_REGISTER():
	op = MEMORY['mem_data'][0:6]
	rs = MEMORY['mem_data'][6:11]
	rt = MEMORY['mem_data'][11:16]
	imm = MEMORY['mem_data'][16:32]
	if (CONTROL_SIGNALS['ir_write']):
		INSTRUCTION_REGISTER['op'] = op
		INSTRUCTION_REGISTER['rs'] = rs
		INSTRUCTION_REGISTER['rt'] = rt
		INSTRUCTION_REGISTER['imm'] = imm
	return

def update_REGISTER_FILE():
	global ALU_OUT
	global MEM_DATA_REG
	rd = INSTRUCTION_REGISTER['imm'][0:5]
	REGISTER_FILE['read_reg_1'] = INSTRUCTION_REGISTER['rs']
	REGISTER_FILE['read_reg_2'] = INSTRUCTION_REGISTER['rt']
	REGISTER_FILE['write_reg'] = reg_dst_MUX(INSTRUCTION_REGISTER['rt'],rd)
	REGISTER_FILE['write_data'] = mem_to_reg_MUX(ALU_OUT, MEM_DATA_REG)
	REGISTER_FILE['read_data_1'] = R[REGISTER_FILE['read_reg_1']]
	REGISTER_FILE['read_data_2'] = R[REGISTER_FILE['read_reg_2']]
	if (CONTROL_SIGNALS['reg_write']):
		R[REGISTER_FILE['write_reg']] = REGISTER_FILE['write_data']
	return

def update_A():
	global REG_A
	REG_A = REGISTER_FILE['read_data_1']
	return

def update_B():
	global REG_B
	REG_B = REGISTER_FILE['read_data_2']
	return

def operate_ALU():
	global REG_A
	global REG_B
	global PC
	funct = INSTRUCTION_REGISTER['imm'][10:16]
	ALU['result'] = ALU_execute(ALU_control(CONTROL_SIGNALS['ALU_op'],funct),ALU_src_A_MUX(PC,REG_A),ALU_src_B_MUX(REG_B,sign_extend(INSTRUCTION_REGISTER['imm'],16),shift_left(sign_extend(INSTRUCTION_REGISTER['imm'],16),2)))
	return

def update_ALU_OUT():
	global ALU_OUT
	ALU_OUT = ALU['result']
	return

def update_PC():
	global PC
	global ALU_OUT
	if (CONTROL_SIGNALS['PC_write'] or (CONTROL_SIGNALS['PC_write_cond'] and ALU['zero'])):
		jump_address = PC[0:4] + shift_left(INSTRUCTION_REGISTER['rs'] + INSTRUCTION_REGISTER['rt'] + INSTRUCTION_REGISTER['imm'],2)
		PC = PC_src_MUX(ALU['result'],ALU_OUT,jump_address)
	return
	