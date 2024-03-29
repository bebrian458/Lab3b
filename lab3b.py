# NAME: Brian Be, Leslie Liang
# EMAIL: bebrian458@gmail.com, lliang9838@gmail.com
# ID: 204612203, 204625818

import sys #For command line args
import csv

class Superblock:
	def __init__(self):
		self.num_blocks = 0
		self.num_inodes = 0
		self.blocksize = 0
		self.inodesize = 0
		self.blocks_per_group = 0
		self.inodes_per_group = 0
		self.first_nr_ino = 0

class Groupdesc:
	def __init__(self):
		self.group_num = 0
		self.g_num_blocks = 0
		self.g_num_inodes = 0
		self.g_num_free_blocks = 0
		self.g_num_free_inodes = 0
		self.g_block_bitmap_num = 0
		self.g_inode_bitmap_num = 0
		self.g_itable_num = 0

class Block:
	def __init__(self, blocknum, blocktype, blockstate, inode_num, offset_num):
		self.blocknum = blocknum
		self.blocktype = blocktype
		self.blockstate = blockstate
		self.inode_num = inode_num
		self.offset_num = offset_num

class Inode:
	def __init__(self, inode_num, numlinks, mode):
		self.inode_num = inode_num
		self.numlinks = numlinks
		self.mode = mode
		self.block_pointers = []
		self.blocks = []

class Dirent:
	def __init__(self, parent_inode_num, child_inode_num, name):
		self.parent_inode_num = parent_inode_num
		self.child_inode_num = child_inode_num
		self.name = name

class Indirect:
	def __init__(self, inode_num, level, block_offset):
		self.inode_num = inode_num
		self.level = level
		self.block_offset = block_offset

# Globals
superblock = Superblock()
groupdesc = Groupdesc()
bfree_list = []
ifree_list = []
inode_list = []
indirect_block_list = []
directory_list = []
allocated_inodes = set()
unallocated_inodes = set()
marked_blocks = set()
block_list = []
start_data_blocks = 1	# change later

def readSuperblock(superblock):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "SUPERBLOCK":
				#print r
				superblock.num_blocks = int(r[1])
				superblock.num_inodes = int(r[2])
				superblock.blocksize = int(r[3])
				superblock.inodesize = int(r[4])
				superblock.blocks_per_group = int(r[5])
				superblock.inodes_per_group = int(r[6])
				superblock.first_nr_ino = int(r[7])

def readGroupdesc(groupdesc):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "GROUP":
				#print r
				groupdesc.group_num = int(r[1])
				groupdesc.g_num_blocks = int(r[2])
				groupdesc.g_num_inodes = int(r[3])
				groupdesc.g_num_free_blocks = int(r[4])
				groupdesc.g_num_free_inodes = int(r[5])
				groupdesc.g_block_bitmap_num = int(r[6])
				groupdesc.g_inode_bitmap_num = int(r[7])
				groupdesc.g_itable_num = int(r[8])

def readBfree(list):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "BFREE":
				list.append(int(r[1]))

def readIfree(list):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "IFREE":
				list.append(int(r[1]))

def readInode(list, list2, list3):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "INODE":
				new_inode = Inode(int(r[1]), int(r[6]), int(r[3]))
				for index in range(12, 24):
					new_inode.block_pointers.append(int(r[index]))
					new_block = Block(int(r[index]), "BLOCK", "NONE", int(r[1]), index-12)
					list3.append(new_block)
					new_inode.blocks.append(new_block)
				new_block = Block(int(r[24]), "INDIRECT BLOCK", "NONE", int(r[1]), 12)
				list3.append(new_block)
				list2.append(new_block)
				new_block = Block(int(r[25]), "DOUBLE INDIRECT BLOCK", "NONE", int(r[1]), 268)
				list2.append(new_block)
				list3.append(new_block)
				new_block = Block(int(r[26]), "TRIPPLE INDIRECT BLOCK", "NONE", int(r[1]), 65804)
				list2.append(new_block)
				list3.append(new_block)
				list.append(new_inode)

def readIndirect(list, list2):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "INDIRECT":
				if r[2] == "1":
					new_block = Block(int(r[5]), "BLOCK", "NONE", int(r[1]), int(r[3]))
					list2.append(new_block)
					list.append(new_block)
				if r[2] == "1":
					new_block = Block(int(r[4]), "INDIRECT BLOCK", "NONE", int(r[1]), int(r[3]))
					# list2.append(new_block)
					list.append(new_block)
				if r[2] == "2":
					new_block = Block(int(r[4]), "DOUBLE INDIRECT BLOCK", "NONE", int(r[1]), int(r[3]))
					# list2.append(new_block)
					list.append(new_block)
				if r[2] == "3":
					new_block = Block(int(r[4]), "TRIPPLE INDIRECT BLOCK", "NONE", int(r[1]), int(r[3]))
					# list2.append(new_block)
					list.append(new_block)

def readDirent(list):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "DIRENT":
				# Check if valid inode num
				if int(r[3]) < 0 or int(r[3]) > superblock.num_inodes or (int(r[3]) > 2 and int(r[3]) < superblock.first_nr_ino):
					print "DIRECTORY INODE", int(r[1]), "NAME", r[6], "INVALID INODE", int(r[3])
				else:
					new_dirent = Dirent(int(r[1]), int(r[3]), r[6])
					list.append(new_dirent)

def isValidBlock(block):
	
	# Check block number
	if block.blocknum < 0 or block.blocknum > superblock.num_blocks:
		block.blockstate = "INVALID"
		# print "INVALID", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num
		return 0

	# Check inode number
	if block.inode_num < 0 or block.inode_num > superblock.num_inodes or (block.inode_num > 2 and block.inode_num < superblock.first_nr_ino):
		block.blockstate = "INVALID"
		print "INVALID", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num
		return 0

	return 1

def checkReserved(block, start_data_blocks):
	if block.blocknum > 0 and block.blocknum < start_data_blocks:
		block.blockstate = "RESERVED"
		# print "RESERVED", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num
		return 1
	return 0

def checkFree(block):
	if block.blocknum in bfree_list:
		block.blockstate = "BFREE"
		# print "ALLOCATED BLOCK", block.blocknum, "ON FREELIST"
		return 1
	return 0

def updateState(block):
	if block.blockstate == "NONE":
		block.blockstate = "IN_USE"
		# print "IN_USE", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num
	elif block.blockstate == "IN_USE" or block.blockstate == "DUPLICATE":
		block.blockstate = "DUPLICATE"
		print "DUPLICATE", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num

def checkBlock(block, start_data_blocks):
	
	'''
	States:
	NONE 	- default
	INVALID - blocknum < 0 or blocknum > numblocks
	VALID:
		RESERVED 	- [1:start of legal data blocks]
		BFREE 		- on the bfree list
		NONE 	-> IN_USE
		IN_USE 	-> DUPLICATE
		DUPLICATE 	- block is referenced multiple times
	UNREFERENCED 	- if after all assignments and state is still none
	'''

	# Assign new states to the block
	if isValidBlock(block) != 1:
		print "INVALID", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num
	else:	
		if checkReserved(block, start_data_blocks) == 1:
			print "RESERVED", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num
		else:	
		 	if checkFree(block) == 1:
		 		print "ALLOCATED BLOCK", block.blocknum, "ON FREELIST"
		 	else:	
				updateState(block)
		marked_blocks.add(block.blocknum)

	# At this point, referenced blocks should be assigned a state other than none
	# if block.blockstate == "NONE":
	# 	block.blockstate = "UNREFERENCED"
	# 	print "UNREFERENCED BLOCK", block.blocknum

def checkMode(inode):
	if inode.mode != 0:
		allocated_inodes.add(inode.inode_num)
	else:
		unallocated_inodes.add(inode.inode_num)

def checkLinkCount(inode):
	ref_count = 0
	for i in directory_list:
		if i.child_inode_num == inode.inode_num:
			ref_count+=1
	if ref_count != inode.numlinks:
		print "INODE", inode.inode_num, "HAS", ref_count, "LINKS BUT LINKCOUNT IS", inode.numlinks

def checkInodeRef(list):
	# Check unallocated node ref
	for i in list:
		if i.child_inode_num in unallocated_inodes:
			print "DIRECTORY INODE", i.parent_inode_num, "NAME", i.name, "UNALLOCATED INODE", i.child_inode_num

	# Check .
	for i in list:
		if i.parent_inode_num != i.child_inode_num and i.name == "'.'":
			print "DIRECTORY INODE", i.parent_inode_num, "NAME", i.name, "LINK TO INODE", i.child_inode_num, "SHOULD BE", i.parent_inode_num

	# Check ..
	for i in list:
		# General case
		if i.parent_inode_num != 2 and i.name == "'..'":
			for j in list:
				if j.child_inode_num == i.parent_inode_num:
					grandparent = j.parent_inode_num
					break;
			if i.child_inode_num != grandparent:
				print "DIRECTORY INODE", i.parent_inode_num, "NAME", i.name, "LINK TO INODE", i.child_inode_num, "SHOULD BE", grandparent
		
		# Root directory special case
		if i.parent_inode_num == 2 and i.name == "'..'":
			if i.child_inode_num != i.parent_inode_num:
				print "DIRECTORY INODE", i.parent_inode_num, "NAME", i.name, "LINK TO INODE", i.child_inode_num, "SHOULD BE", i.parent_inode_num

def checkDuplicates(list):
	
	for i in range(len(list)):
		if isValidBlock(list[i]) == 1 and list[i].blocknum != 0:
			if checkReserved(list[i], start_data_blocks) != 1:
				if checkFree(list[i]) != 1:
					temp = []
					temp.append(list[i])
					counter = i + 1
					for j in range (counter,len(list)):
						if list[j].blocknum == list[i].blocknum:
							temp.append(list[j])
					if len(temp) > 1:
						for block in temp:
							print "DUPLICATE", block.blocktype, block.blocknum, "IN INODE", block.inode_num, "AT OFFSET", block.offset_num




def main():
	# sys.stdout.write("The input file name is: " + str(arg1) + '\n')
	readSuperblock(superblock)
	#print superblock.blocksize
	readGroupdesc(groupdesc)
	readBfree(bfree_list)
	readIfree(ifree_list)
	readInode(inode_list, indirect_block_list, block_list)
	readIndirect(indirect_block_list, block_list)
	readDirent(directory_list)

	# Identify start of legal data blocks
	blocks_occupied_by_itable = (superblock.inodesize*superblock.inodes_per_group)/superblock.blocksize
	start_data_blocks =  blocks_occupied_by_itable + groupdesc.g_itable_num

	# Mark all reserved blocks
	for i in range (1, start_data_blocks):
		marked_blocks.add(i)

	# Check validity of ever block in inode
	for i in inode_list:
		checkMode(i)
		checkLinkCount(i)
		for index in range (0,12):	# might be 0-15, but will then need to take care of duplicates
			if i.blocks[index] != 0:
				checkBlock(i.blocks[index], start_data_blocks)

	# TODO: fix
	for i in indirect_block_list:
		checkBlock(i, start_data_blocks)

	# Print unreferenced blocks
	for blocknum in range (1, superblock.num_blocks):
			if not blocknum in bfree_list and not blocknum in marked_blocks:
				print "UNREFERENCED BLOCK", blocknum

	# All reserved inodes should be in the allocated list
	for i in range (1, superblock.first_nr_ino):
		allocated_inodes.add(i)

	# All inodes on ifree list should be in unallocated list
	# Make sure unallocated inodes do not contain allocated inodes
	for i in ifree_list:
		if not i in allocated_inodes:
			unallocated_inodes.add(i)

	# Every unreferenced inode should be in unallocated list
	for i in range (1, superblock.num_inodes):
		if not i in allocated_inodes and not i in unallocated_inodes:
			unallocated_inodes.add(i)

	# Allocated inodes should not be on freelist
	for i in allocated_inodes:
		if i in ifree_list:
			print "ALLOCATED INODE", i, "ON FREELIST"

	# Unallocated inodes should be on freelist
	for i in unallocated_inodes:
		if not i in ifree_list:
			print "UNALLOCATED INODE", i, "NOT ON FREELIST"

	# Check inode ref
	checkInodeRef(directory_list)

	# for i in block_list:
	# 	print i.blocknum

	checkDuplicates(block_list)

	# for i in indirect_block_list:
	# 	print i.blocknum, i.blockstate

	# print "Printing block list"
	# for i in block_list:
	# 	print i.blocktype, i.blocknum

	# print "Printing indirect_block_list"
	# for i in indirect_block_list:
	# 	print i.blocktype, i.blocknum

	

if __name__ == '__main__':
	try:
		arg1 = sys.argv[1]
		main()
	except IndexError:
		print "Invalid arguments. Usage: lab3b <filename.csv>"
        sys.exit(1) 
