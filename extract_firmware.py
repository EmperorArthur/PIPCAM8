#PIPCAM8 Firmware Extractor
#Copyright Arthur Moore 2015
#BSD 3 Clause License

from struct import *
import os
import sys

#File Name:
#   44 bytes total
#   File Name 28 bytes (28 chars)
#   ??? 4 bytes
#   File Start location 4 bytes (1 unsigned int)
#   File size 4 bytes (1 unsigned int)
#   Folder Select 4 bytes (1 unsigned int)

#File contents
#   total size (see File Name)
#   ??? 3 bytes
#   File actual contents (rest)

class packed_file:
    def __init__(self, inFile = None, folder_names = None):
        self.name = ''
        self.unkown_int = 0
        self.file_start = 0
        self.size = 0
        self.folder_select = 0
        self.folder_name = ''
        self.contents_header = ''
        self.contents = ''
        if(inFile):
            #This comes from the file name struct
            unpacked_struct = unpack('28s4I', inFile.read(44))
            self.name = unpacked_struct[0].rstrip('\0')
            self.unkown_int = unpacked_struct[1]
            self.file_start = unpacked_struct[2]
            self.size = unpacked_struct[3]
            self.folder_select = unpacked_struct[4]
            if(folder_names):
                self.folder_name = folder_names[self.folder_select]
            #Read the file contents
            original_position = inFile.tell()
            inFile.seek(self.file_start,0)
            tmp = inFile.read(self.size)
            self.contents_header = tmp[0:2]
            self.contents = tmp[3:]
            inFile.seek(original_position,0)


#A quick check to make sure all the padding read is really '0x00'
def Read_padding(inFile,size):
    padding = inFile.read(size)
    if(padding != size*'\x00'):
        raise Exception('Padding not all zeros')

#Extract the packed files
def Extract(packed_files):
    try:
        os.mkdir("Extracted")
    except:
        pass
    os.chdir("Extracted")
    for i in range(0,len(packed_files)):
        tmp_file = packed_files[i]
        if(tmp_file.folder_name == ''):
            print('Extracting: ' + tmp_file.name)
            outFile = open(tmp_file.name, "wb")
            outFile.write(tmp_file.contents)
            outFile.close()
        else:
            print ('Extracting: ' + tmp_file.folder_name + '/' + tmp_file.name)
            try:
                os.mkdir(tmp_file.folder_name)
            except:
                pass
            os.chdir(tmp_file.folder_name)
            outFile = open(tmp_file.name, "wb")
            outFile.write(tmp_file.contents)
            outFile.close()
            os.chdir('..')
    os.chdir('..')

#Get all the packed files
def Get_files(in_file_name):
    #Variable declaration
    num_folders = 0     #The number of folders in the packed file
    folder_names = []   #The name of each folder (order is important)
    num_files = 0       #The number of files in the packed file
    packed_files = []   #The packed files (done in two separate steps)

    inFile = open(in_file_name, "rb")

    #Make sure we have a valid header
    header = inFile.read(8)
    if(header != 'apexapcf' and header != 'apexapsf'):
        raise Exception('Invalid File Header')

    Read_padding(inFile,32)

    #Get the number of folders
    num_folders = unpack('I',inFile.read(4))[0]

    #Get all the folder names
    for i in range(0,num_folders):
        folder_names.append(unpack('32s',inFile.read(32))[0].rstrip('\0'))

    #Skip to the start of file list
    inFile.seek(0x02AC)

    #Get the number of files
    num_files = unpack('I',inFile.read(4))[0]

    Read_padding(inFile,4)

    #Get all the files
    for i in range(0,num_files):
        packed_files.append(packed_file(inFile,folder_names))
    return packed_files

packed_files = Get_files(str(sys.argv[1]))
Extract(packed_files)
