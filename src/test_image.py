from ast import Bytes
from PIL import Image
from io import BytesIO
import base64

with open("original.txt","r") as f:
    img = Image.open(BytesIO(base64.b64decode(f.read())))
    output_buffer = BytesIO()
    basewidth=500
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), Image.Resampling.LANCZOS)
    #img.save("optimized.png", optimize=True, quality=80)
    img.save(output_buffer, optimize=True, quality=80, format='PNG')
    
    output_buffer.seek(0)
    print(base64.b64encode(output_buffer.read())[:100].decode('utf-8'))
