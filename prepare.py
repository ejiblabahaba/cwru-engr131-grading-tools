import os, os.path
import re
import shutil
import sys
from zipfile import ZipFile, BadZipFile

HWPATH = sys.argv[1]
if len(sys.argv) > 2: STUDENTS = sys.argv[2]
else: STUDENTS = 'students.txt'

def move_to_caseid(new_dir, hw_archive, cid, everyone={}):
	try:
		HW = ZipFile(os.path.join(new_dir,hw_archive))
		HW.extractall(new_dir)
		HW.close()
		os.remove(os.path.join(new_dir,hw_archive))
	except BadZipFile:
		sys.stderr.write("File {0} appears to be broken...\r\n".format(hw_archive))

	files = list(everyone.keys())
	their_files = os.listdir(new_dir)
	for f in files:
		if f in their_files:
			os.remove(os.path.join(new_dir,f))
		shutil.copy(everyone[f],new_dir)

def get_caseids(filename):
	try:
		with open(filename) as f:
			case_ids = [x.strip() for x in f.readlines()]
		return case_ids
	except FileNotFoundError:
		sys.stderr.write("No students file found, unzipping all instead...\r\n")
		return []

def get_everyone(path):
	trupath = os.path.join('.',path,'everyone')
	try:
		return {f:os.path.join(trupath,f) for f in os.listdir(trupath)}
	except FileNotFoundError:
		sys.stderr.write("No ubiquitous files found.\r\n")
		return {}

if __name__ == '__main__':
	case_ids = get_caseids(STUDENTS)
	everyone = get_everyone(HWPATH)
	zipname = list(x for x in os.listdir(os.path.join('.',HWPATH))
		if x.endswith('.zip'))
	hwzip = ZipFile(os.path.join('.',HWPATH,zipname[0]))
	zips = [x for x in hwzip.namelist() if x.endswith('.zip')]
	rars = [x for x in hwzip.namelist() if x.endswith('.rar')]
	_7zs = [x for x in hwzip.namelist() if x.endswith('.7z')]
	cid_re = re.compile(r'_[a-z]{3}[0-9]{0,4}')
	if case_ids != []:
		zips = [x for x in zips for y in case_ids if (re.search(y,x) != None)]
	else:
		case_ids = [cid_re_re.findall(zips[i])[0][1:] for i in range(len(zips))]
	case_ids.sort()
	zips.sort()
	for (cid, zfile) in zip(case_ids,zips):
		new_dir = os.path.join('.',HWPATH,cid)
		os.mkdir(new_dir)
		hwzip.extract(zfile,new_dir)
		move_to_caseid(new_dir, zfile, cid, everyone)
	hwzip.close()
	rars_ids = [cid_re.findall(rars[i])[0][1:] for i in range(len(rars))]
	_7zs_ids = [cid_re.findall(_7zs[i])[0][1:] for i in range(len(_7zs))]
	has_rar = set(rars_ids) & set(case_ids)
	has_7z = set(_7zs_ids) & set(case_ids)
	if STUDENTS != 'students.txt' and (rars_ids != [] or _7zs_ids != []):
		sys.stderr.write("Users with unsupported formats:\r\n{0}\r\n".format(rars_ids+_7zs_ids))
	elif len(has_rar) > 0:
		sys.stderr.write("The following jerk(s) use rar: \r\n{0}\r\n".format(list(has_rar)))
	elif len(has_7z) > 0:
		sys.stderr.write("The following jerk(s) use 7z: \r\n{0}\r\n".format(list(has_7z)))
	sys.stderr.write("All done.")
