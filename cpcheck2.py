from PIL import Image
import hashlib
for i in [1,2]:
    img=Image.open('/home/net77/koedit/export/%04d.png'%i)
    h=hashlib.md5(img.tobytes()).hexdigest()
    print('export/%04d.png: md5=%s size=%s'%(i,h,img.size))
for i in [1,2]:
    img=Image.open('/home/net77/koedit/originals/%04d.png'%i)
    h=hashlib.md5(img.tobytes()).hexdigest()
    print('originals/%04d.png: md5=%s size=%s'%(i,h,img.size))
