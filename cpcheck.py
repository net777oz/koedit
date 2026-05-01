from PIL import Image
import numpy as np
PALETTE=[(0,0,0),(0,0xA2,0x61),(0xD3,0x41,0),(0xF3,0xA2,0x61),(0,0x41,0xD3),(0,0xA2,0xF3),(0xD3,0x61,0xA2),(0xF3,0xE3,0xD3)]
def qfn(img):
    a=np.array(img.resize((64,80)).convert('RGB'),dtype=np.float32)
    p=np.array(PALETTE,dtype=np.float32)
    b=np.argmin(np.sum((a[:,:,None,:]-p[None,None,:,:])**2,axis=3),axis=2)
    return np.array(PALETTE,dtype=np.uint8)[b]
for i,name in [(1,'Joan'),(2,'Catalina')]:
    img=Image.open('/home/net77/koedit/export/%04d.png'%i)
    print(name,img.size,img.mode)
    qd=qfn(img)
    sigs=[]
    for py in range(5,75,7):
        for px in range(5,59,7):
            r,g,b=int(qd[py,px][0]),int(qd[py,px][1]),int(qd[py,px][2])
            if r+g+b>50:
                sigs.append((px,py,r,g,b))
                if len(sigs)>=10:break
        if len(sigs)>=10:break
    print('  sigs:',len(sigs),'OK' if len(sigs)>=5 else 'FAIL-wont-match')
    print(' ',sigs)
