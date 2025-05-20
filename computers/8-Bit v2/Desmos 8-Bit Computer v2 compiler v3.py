import sys
import re
from bitstring import Bits
file_path = 'test CAL.dasm'
if len(sys.argv) > 1:
    file_path = sys.argv[1]
opcodes = {'NOP': '0000', 'HLT': '0001', 'ADD': '0010', 'SUB': '0011', 'NOR': '0100', 'AND': '0101', 'XOR': '0110', 'RSH': '0111', 
           'LDI': '1000', 'ADI': '1001', 'JMP': '1010', 'BRH': '1011', 'CAL': '1100', 'RET': '1101', 'LOD': '1110', 'STR': '1111'}
#print(opcodes.keys(), len(opcodes))
psuedocodes = {'INC': opcodes['ADI'], 'DEC': opcodes['ADI'], 'CMP': opcodes['SUB'], 'MOV': opcodes['ADD'], 'LSH': opcodes['ADD'],
               'NOT': opcodes['NOR'], 'NEG': opcodes['SUB']}
opcodes |= psuedocodes
comps = {'zero': '00', 'notzero': '01', 'carry': '10', 'notcarry': '11', 
         '=': '00', '!=': '01', '>=': '10', '<': '11', 
         'z': '00', 'nz': '01', 'c': '10', 'nc': '11',
         'eq': '00', 'ne': '01', 'ge': '10', 'lt': '11'}
ports = ['pixel_x', 'pixel_y', 'draw_pixel', 'clear_pixel', 'load_pixel', 'buffer_screen', 'clear_screen_buffer', 'write_char', 
         'buffer_chars', 'clear_chars_buffer', 'show_number', 'clear_number', 'signed_mode', 'unsigned_mode', 'rng', 'controller_input']
charLookup = {'_': 0, '.': 27, '!': 28, '?':29}
for i in range(26):
    charLookup['abcdefghijklmnopqrstuvwxyz'[i]] = i+1
labels = {}
definitions = {}
for i in range(len(ports)):
    definitions[ports[i]] = 240 + i

if file_path[-1] != 'm':
    # Pre-Processing
    with open(file_path, 'r') as inputFile:
        file = inputFile.read()
    with open(file_path.rpartition('.')[0]+'.dasm', 'w') as inputFile:
        inputFile.write(file.replace('//', ';').replace('" "', '"_"').replace('define', '#define'))
    print('Converted .as file to .dasm!')
    quit()

class Instruction():
    def __init__(self, opcode, format: str):
        self.opcode = opcode
        self.formatCode = format
    def input(self, operands: str):
        ops = operands.split(' ')
        binary = {}
        #print(ops, operands)
        for op in ops:
            if len(op) == 0:
                continue
            if op.startswith('r') and op[1].isnumeric():
                binary[f'r{len(binary)}'] = format(int(op[1:]), '04b')
            elif op in list(comps.keys()):
                binary['cond'] = comps[op]
            elif re.match('^-?[0-9]+$', op):
                if int(op) < 0:
                    binary['immediate'] = Bits(int=int(op), length=8).bin
                else: 
                    binary['immediate'] = Bits(uint=int(op), length=8).bin
            elif re.match('(^[A-Za-z_0-9]+$)|^"[A-Za-z_!?.]{1}"$', op):
                if op in definitions:
                    if self.opcode in ['ADI', 'LDI']:
                        binary['immediate'] = Bits(uint=int(definitions[op]), length=8).bin
                    elif self.opcode in ['LOD', 'STR']:
                        binary['off'] = Bits(int=int(definitions[op]), length=4).bin
                elif op[0:2] == '0b':
                    binary['immediate'] = op[2:]
                elif op[0] == '"':
                    binary['immediate'] = format(int(charLookup[op[1].lower()]), '08b')
            elif op[0] == '.':
                binary['address'] = format(int(labels[op]), '010b')
            if self.opcode in ['LOD', 'STR'] and not 'off' in binary and len(binary) >= 2:
                binary['off'] = '0000'
        #print(self.opcode, operands, ops, binary)
        return (opcodes[self.opcode] + self.formatCode.format(**binary)).replace(' ', '')

NOP = Instruction('NOP', '000000000000')
HLT = Instruction('HLT', '000000000000')
ADD = Instruction('ADD', '{r0}{r1}{r2}')
SUB = Instruction('SUB', '{r0}{r1}{r2}')
NOR = Instruction('NOR', '{r0}{r1}{r2}')
AND = Instruction('AND', '{r0}{r1}{r2}')
XOR = Instruction('XOR', '{r0}{r1}{r2}')
RSH = Instruction('RSH', '{r0}0000{r1}')
LDI = Instruction('LDI', '{r0}{immediate}')
ADI = Instruction('ADI', '{r0}{immediate}')
JMP = Instruction('JMP', '00{address}')
BRH = Instruction('BRH', '{cond}{address}')
CAL = Instruction('CAL', '00{address}')
RET = Instruction('RET', '000000000000')
LOD = Instruction('LOD', '{r0}{r1}{off}')
STR = Instruction('STR', '{r0}{r1}{off}')

CMP = Instruction('CMP', '{r0}{r1}0000')
MOV = Instruction('MOV', '{r0}0000{r1}')
LSH = Instruction('LSH', '{r0}{r0}{r1}')
INC = Instruction('INC', '{r0}00000001')
DEC = Instruction('DEC', '{r0}11111111')
NOT = Instruction('NOT', '{r0}0000{r1}')
NEG = Instruction('NEG', '0000{r0}{r1}')

instructions = {'NOP': NOP, 'HLT': HLT, 'ADD': ADD, 'SUB': SUB, 'NOR': NOR, 'AND': AND, 'XOR': XOR, 'RSH': RSH,
                'LDI': LDI, 'ADI': ADI, 'JMP': JMP, 'BRH': BRH, 'CAL': CAL, 'RET': RET, 'LOD': LOD, 'STR': STR,
                'CMP': CMP, 'MOV': MOV, 'LSH': LSH, 'INC': INC, 'DEC': DEC, 'NOT': NOT, 'NEG': NEG}

with open(file_path, 'r') as inputFile:
    i = 0
    with open(file_path.rpartition('.')[0]+'.bin', 'w') as outputFile:
        for line in inputFile:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '.':
                labels[line.replace('\n','').split(' ')[0]] = i
                #print(labels)
            elif line[0:8] == '#define ':
                defined = line[8:].replace('\n','').split(' ')
                definitions[defined[0]] = defined[1]
                #print(definitions)
            elif line[0] in ['\n', ';']:
                pass
            else:
                i += 1
        inputFile.seek(0)
        for i, line in enumerate(inputFile):
            line = line.strip()
            if len(line) == 0 or line[0] in ['#', ';', '\n', '.']:
                continue
            opcode = line[:3]
            operands = ''
            try:
                operands += line[4: line.index(';')].strip()
            except ValueError:
                if len(line) > 3:
                    operands += line[4:-1] + line[-1]
            outputFile.write(instructions[opcode].input(operands))
            outputFile.write(f'    {i}')
            outputFile.write('\n')