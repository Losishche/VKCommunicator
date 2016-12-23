__author__ = 'grishaev'

import sys, os
import math
import string
#import Image
import PIL.ImageChops

from PIL import Image
from operator import itemgetter

im = Image.open("6.jpg")
print(help(im.convert))
im = im.convert("L", dither=10)
his = im.histogram()


im.show()
for color in range(0,256):
    print(im.getcolors(color))


print(im.histogram())

values = {}
for i in range(256):
  values[i] = his[i]

for j,k in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
  print(j,k)

im2 = Image.new("L",im.size,256)
#im = im.convert("P")

temp = {}

lis = []
for x in range(256):
    if x  in [218, 219, 220, 217, 242] :
        lis.append(x)

for x in range(im.size[1]):
  for y in range(im.size[0]):
    pix = im.getpixel((y,x))
    temp[pix] = pix
    if pix in lis: # these are the numbers to get
      im2.putpixel((y,x),0)

im2.save("output.gif")

'''

from urllib2 import urlopen
from urllib import urlretrieve
from PIL import Image, ImageOps, ImageEnhance
import os
import sys
import re
import time

def main(url, n):
    # get url session url
    data = urlopen(url).read()
    match = re.search(r"/random/images/\?session=[a-z0-9]+\&quot;, data)
    if match:
   imgurl = "ifolder.ru" + match.group()
    else:
   return -1

    # gen imgs
    for i in range(n):
        urlretrieve(imgurl, '/test/' + str(i) + '.gif')
        time.sleep(1)
        print str(i) + ' of ' + str(n) + ' downloaded'

    # convert them
    for i in range(n):
        img = Image.open('/test/' + str(i) + '.gif').convert('L')
        img = ImageOps.invert(img)
        img = ImageEnhance.Contrast(img).enhance(1.9)
        img.save('/test/' + str(i) + '.bmp')
        #os.unlink('/test/' + str(i) + '.gif')


if __name__ == "__main__":
    url = sys.argv[-1]
    if not url.lower().startswith("http"):
        print "usage: python dumpimages.py http://ifolder.com/?num"
        sys.exit(-1)
    main(url, 500)


if __name__=="__main__":
    input = sys.argv[1]
    base = Image.open(input).convert('L')

    class Fit:
        letter = None
        difference = 0

    best = Fit()

    for letter in string.lowercase:
        current = Fit()
        current.letter = letter

        sample_path = os.path.join('samples', letter + '.png')
        sample = Image.open(sample_path).convert('L').resize(base.size)
        difference = PIL.ImageChops.difference(base, sample)

        for x in range(difference.size[0]):
            for y in range(difference.size[1]):
                current.difference += difference.getpixel((x, y))

        if not best.letter or best.difference > current.difference:
            best = current

    print (best.letter)'''