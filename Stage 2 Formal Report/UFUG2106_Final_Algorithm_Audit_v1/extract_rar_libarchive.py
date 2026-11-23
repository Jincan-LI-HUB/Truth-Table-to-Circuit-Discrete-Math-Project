import ctypes as c, pathlib, sys
lib=c.CDLL('libarchive.so.13')
for name,restype,args in [
 ('archive_read_new',c.c_void_p,[]),('archive_read_support_filter_all',c.c_int,[c.c_void_p]),('archive_read_support_format_all',c.c_int,[c.c_void_p]),('archive_read_open_filename',c.c_int,[c.c_void_p,c.c_char_p,c.c_size_t]),('archive_read_next_header',c.c_int,[c.c_void_p,c.POINTER(c.c_void_p)]),('archive_entry_pathname',c.c_char_p,[c.c_void_p]),('archive_entry_filetype',c.c_uint,[c.c_void_p]),('archive_read_data',c.c_ssize_t,[c.c_void_p,c.c_void_p,c.c_size_t]),('archive_read_free',c.c_int,[c.c_void_p]),('archive_error_string',c.c_char_p,[c.c_void_p])]:
 f=getattr(lib,name);f.restype=restype;f.argtypes=args
src,dst=pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]);dst.mkdir(parents=True,exist_ok=True)
a=lib.archive_read_new();lib.archive_read_support_filter_all(a);lib.archive_read_support_format_all(a)
assert lib.archive_read_open_filename(a,str(src).encode(),10240)==0,lib.archive_error_string(a)
e=c.c_void_p(); n=0
while True:
 status=lib.archive_read_next_header(a,c.byref(e))
 if status==1:break
 if status!=0:raise RuntimeError(('next header',status,lib.archive_error_string(a)))
 name=lib.archive_entry_pathname(e).decode('utf-8',errors='replace')
 path=pathlib.PurePosixPath(name.replace('\\','/'))
 if path.is_absolute() or '..' in path.parts: raise ValueError('unsafe '+name)
 target=dst.joinpath(*path.parts)
 if lib.archive_entry_filetype(e)&0o170000==0o40000 or name.endswith('/'):
  target.mkdir(parents=True,exist_ok=True);continue
 target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('wb') as out:
  buf=c.create_string_buffer(1<<16)
  while True:
   ret=lib.archive_read_data(a,buf,len(buf))
   if ret<0:raise RuntimeError(('read data',name,lib.archive_error_string(a)))
   if ret==0:break
   out.write(buf.raw[:ret])
 n+=1
lib.archive_read_free(a)
print('EXTRACTED',n,'files to',dst)
