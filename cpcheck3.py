from PIL import Image
import numpy as np
PALETTE=[(0,0,0),(0,0xA2,0x61),(0xD3,0x41,0),(0xF3,0xA2,0x61),(0,0x41,0xD3),(0,0xA2,0xF3),(0xD3,0x61,0xA2),(0xF3,0xE3,0xD3)]
def qfn(img):
    a=np.array(img.resize((64,80)).convert('RGB'),dtype=np.float32)
    p=np.array(PALETTE,dtype=np.float32)
    b=np.argmin(np.sum((a[:,:,None,:]-p[None,None,:,:])**2,axis=3),axis=2)
    return np.array(PALETTE,dtype=np.uint8)[b]

# Compare full pixel data
q1=qfn(Image.open('/home/net77/koedit/export/0001.png'))
q2=qfn(Image.open('/home/net77/koedit/export/0002.png'))
diff=np.sum(q1!=q2)
print('Total pixel channel diffs between Joan and Catalina quantized 64x80:',diff)
print('Same pixels?', diff==0)

# Show first 10 rows that differ
for y in range(80):
    row_diff=np.any(q1[y]!=q2[y],axis=1)
    if np.any(row_diff):
        print('First diff at row y=%d'%y)
        break

# Show the SAD (sum of absolute diffs)
sad=int(np.sum(np.abs(q1.astype(np.int32)-q2.astype(np.int32))))
print('SAD:',sad,'(threshold in code is 35000)')
