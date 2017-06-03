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



def readSuperblock(superblock):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "SUPERBLOCK":
				#print r
				superblock.num_blocks = r[1]
				superblock.num_inodes = r[2]
				superblock.blocksize = r[3]
				superblock.inodesize = r[4]
				superblock.blocks_per_group = r[5]
				superblock.inodes_per_group = r[6]
				superblock.first_nr_ino = r[7]

def readGroupdesc(groupdesc):
	with open(arg1, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for r in reader:
			if r[0] == "GROUP":
				#print r
				groupdesc.group_num = r[1]
				groupdesc.g_num_blocks = r[2]
				groupdesc.g_num_inodes = r[3]
				groupdesc.g_num_free_blocks = r[4]
				groupdesc.g_num_free_inodes = r[5]
				groupdesc.g_block_bitmap_num = r[6]
				groupdesc.g_inode_bitmap_num = r[7]
				groupdesc.g_itable_num = r[8]



def main():
	print "The input file name is:", arg1
	superblock = Superblock()
	groupdesc = Groupdesc()
	readSuperblock(superblock)
	# print superblock.num_blocks
	# print superblock.num_inodes
	# print superblock.blocksize
	# print superblock.inodesize
	# print superblock.blocks_per_group
	# print superblock.inodes_per_group
	# print superblock.first_nr_ino
	readGroupdesc(groupdesc)
	# print groupdesc.group_num
	# print groupdesc.g_num_blocks
	# print groupdesc.g_num_inodes
	# print groupdesc.g_num_free_blocks
	# print groupdesc.g_num_free_inodes
	# print groupdesc.g_block_bitmap_num
	# print groupdesc.g_inode_bitmap_num
	# print groupdesc.g_itable_num



if __name__ == '__main__':
	try:
		arg1 = sys.argv[1]
		main()
	except IndexError:
		print "Invalid arguments. Usage: lab3b <filename.csv>"
        sys.exit(1) 
