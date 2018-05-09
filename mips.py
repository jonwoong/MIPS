########## IMPORTS ##########

import pprint
import os
import sys

sys.path.append(os.path.abspath('../single_cycle.py'))
sys.path.append(os.path.abspath('../multi_cycle.py'))

import single_cycle as sc
import multi_cycle as mc

########## GLOBALS ##########

INSN_MEM = {} # instruction memory
MEM = [] # memory

########## DATA STRUCTS ##########

INSTRUCTION = { 
	'add':
		{'op':'000000',
		'shamt':'00000',
		'funct':'100000',
		'type':'R'},
	'addi':{
		'op':'001000',
		'type':'I'},
	'beq':{
		'op':'000100',
		'type':'I'},
	'bne':{
		'op':'000101',
		'type':'I'},
	'j':{
		'op':'000010',
		'type':'J'},
	'jal':{
		'op':'000011'},
	'jr':{
		'op':'000000',
		'rt':'00000',
		'rd':'00000',
		'shamt':'00000',
		'funct':'001000'},
	'lb':{
		'op':'100000'},
	'lui':{
		'op':'001111',
		'type':'I'},
	'lw':{
		'op':'100011',
		'type':'I'},
	'or':{
		'op':'000000',
		'shamt':'00000',
		'funct':'100101'},
	'sb':{
		'op':'101000'},
	'sll':{
		'op':'000000',
		'funct':'000000'},
	'slt':{
		'op':'000000',
		'shamt':'00000',
		'funct':'101010'},
	'slti':{
		'op':'001010'},
	'sltu':{
		'op':'000000',
		'shamt':'00000',
		'funct':'101011'},
	'srl':{
		'op':'000000',
		'funct':'000010'},
	'sw':{
		'op':'101011',
		'type':'I'},
	'xor':{
		'op':'000000',
		'funct':'100110'}
	}

########## FUNCTIONS ##########

##### HELPER #####

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

def binary_instruction(name,rs=0,rt=0,rd=0,imm_val=0,offset_val=0,target_val=0):
	op_binary = INSTRUCTION[name]['op']
	s_binary = to_binary('reg',rs)
	t_binary = to_binary('reg',rt)

	insn_type = INSTRUCTION[name]['type']
	if (insn_type=='R'):
		return name, insn_type, op_binary + s_binary + t_binary + to_binary('reg',rd) + INSTRUCTION[name]['shamt'] + INSTRUCTION[name]['funct']
	elif (insn_type=='I'):
		return name, insn_type, op_binary + s_binary + t_binary + to_binary('imm',imm_val)
	elif (insn_type=='J'):
		return name, insn_type, op_binary + to_binary('target',target_val)

##### MIPS to binary #####

def add(d,s,t):
	return binary_instruction('add',rs=s,rt=t,rd=d)

def addi(t,s,imm):
	return binary_instruction('addi',rs=s,rt=t,imm_val=imm)

def beq(s,t,offset):
	global PC
	if (R[s]==R[t]):
		PC += (offset<<2)
	else:
		PC += 4
	return

def bne(s,t,offset):
	global PC
	if (R[s]!=R[t]):
		PC += (offset<<2)
	else:
		PC += 4
	return

def j(target):
	return binary_instruction('j',target_val=target)

def jr(s):
	global PC
	PC = R[s]
	return

def lui(t,imm):
	return binary_instruction('lui',rt=t,imm_val=imm)

def lw(t,offset,s):
	global PC, MEM
	R[t] = MEM[R[s]+offset]
	PC += 4
	return

def sb(t,offset,s):
	global PC, MEM
	MEM[R[s]+offset] = (0xff & R[t])
	PC += 4
	return

def sll(d,t,imm):
	global PC
	R[d] = R[t] << imm
	PC += 4
	return

def slt(d,s,t):
	global PC
	if (R[s] < R[t]):
		R[d] = 1
	else:
		R[d] = 0
	PC += 4
	return

def slti(t,s,imm):
	global PC
	if (R[s] < imm):
		R[t] = 1
	else:
		R[t] = 0
	PC += 4
	return

def sltu(d,s,t):
	global PC
	if (R[s] < R[t]):
		R[d] = 1
	else:
		R[d] = 0
	PC += 4
	return

def srl(d,t,imm):
	global PC
	R[d] = R[t] >> imm
	PC += 4
	return

def sw(t,offset,s):
	global PC
	MEM[R[s]+offset] = R[t]
	PC += 4
	return

def xor(d,s,t):
	global PC
	R[d] = R[s] ^ R[t]
	PC += 4
	return

########## MODULES ##########

def ALU_control(op,funct):
	if (op=='00'): # LW/SW
		return '0010'
	elif (op=='01'): # BEQ
		return '0110'
	elif (op=='10'): # R-type
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

def ALU(op,a,b):
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
			ALU_SIGNALS['zero'] = '1'
		else:
			ALU_SIGNALS['zero'] = '0'
		return to_binary((int(a,2)-int(b,2)),32)
	elif (op=='1100'): # NOR
		return to_binary(not(int(a,2)|int(b,2)),32)

########## CLASSES ##########

# single cycle implementation
class single_cycle:

	def __init__(self,PC):
		self.PC = PC
		initialize_registers()
		return

	def execute(self): # name, type, binary
		##### IF
		# fetch insn
		instruction = INSN_MEM[self.PC]
		#print instruction

		# get fields
		op = instruction[0:6]
		rs = instruction[6:11]
		rt = instruction[11:16]
		rd = instruction[16:21]
		imm = instruction[16:32]
		funct = instruction[26:32]
		j_target = instruction[6:32]

		# increment PC
		inc_PC = binary_add(self.PC,to_binary('int',4))

		##### ID
		# generate control signals
		sc.control(op) 

		# set register file
		RF_rr_1 = rs # read reg 1
		RF_rr_2 = rt # read reg 2
		RF_wr = sc.reg_dst_MUX(rt,rd,SS_CONTROL_SIGNALS['reg_dst']) # write reg
		RF_rd_1 = R[RF_rr_1] # read data 1
		RF_rd_2 = R[RF_rr_2] # read data 2
		sc.set_register_file(rr1=RF_rr_1,rr2=RF_rr_2,wr=RF_wr,rd1=RF_rd_1,rd2=RF_rd_2)

		##### EX
		# alu compute
		ALU_result = sc.ALU(sc.ALU_control(SS_CONTROL_SIGNALS['ALU_op'],funct),RF_rd_1,sc.ALU_src_MUX(RF_rd_2,sign_extend(imm,16),SS_CONTROL_SIGNALS['ALU_src']))

		# branch handle
		branch_MUX_output = sc.branch_MUX(inc_PC,binary_add(inc_PC,shift_left(sign_extend(imm,16),2)),sc.branch_AND(SS_CONTROL_SIGNALS['branch'],ALU_UNIT['zero']))
		self.PC = sc.jump_MUX(branch_MUX_output,sc.calculate_jump_addr(j_target,inc_PC),SS_CONTROL_SIGNALS['jump'])

		##### MEM
		# set register file write data
		mem_to_reg_MUX_output = sc.mem_to_reg_MUX(ALU_result,sc.data_memory_logic(ALU_result,RF_rd_2,SS_CONTROL_SIGNALS['mem_write'],SS_CONTROL_SIGNALS['mem_read']),SS_CONTROL_SIGNALS['mem_to_reg'])
		RF_wd = sc.ui_to_reg_MUX(mem_to_reg_MUX_output,imm,SS_CONTROL_SIGNALS['ui_to_reg'])

		##### WB
		# update register file
		sc.update_register_file(SS_CONTROL_SIGNALS['reg_write'],RF_wd)

# multi cycle implementation
class multi_cycle:
	def __init__(self,PC):
		mc.PC = PC
		return

	def add_instruction(self,instruction):
		mc.DATA_MEMORY[mc.PC] = instruction
		return

	def cycle(self):
		mc.update_MEMORY()
		mc.update_INSTRUCTION_REGISTER()
		mc.update_REGISTER_FILE()
		mc.update_A()
		mc.update_B()
		mc.operate_ALU()
		mc.update_ALU_OUT()
		mc.update_PC()
		return

	def instruction_fetch(self):
		mc.generate_fetch_signals()
		self.cycle()
		return

	def instruction_decode(self):
		mc.generate_decode_signals()
		self.cycle()
		return

	def execute(self):
		mc.generate_execute_signals()
		self.cycle()
		return

	def memory(self):
		mc.generate_memory_signals()
		self.cycle()
		return

	def write_back(self):
		mc.generate_write_back_signals()
		self.cycle()
		return

	def run(self):
		self.instruction_fetch()
		self.instruction_decode()
		self.execute()
		if (mc.CURRENT_INSN[1] != 'J' or mc.CURRENT_INSN[0] != 'beq'):
			self.memory()
			if (mc.CURRENT_INSN[0] == 'lw'):
				self.write_back()
		return

########## MAIN ##########

if __name__ == "__main__":

	pp = pprint.PrettyPrinter(indent=2)

	PC = mc.to_binary('int',0)

	multi = multi_cycle(PC)
	mc.set_register(1,100)
	mc.set_register(2,200)
	mc.set_register(3,0)
	multi.add_instruction(add(3,1,2))
	multi.run()

	pp.pprint(mc.R)
	print int(mc.R['00001'],2),int(mc.R['00010'],2),int(mc.R['00011'],2)
	
	



