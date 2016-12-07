import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import sys
import argparse
try:
    from PIL import Image
except ImportError:
    import Image

# Open image file

ap = argparse.ArgumentParser()
ap.add_argument('--f', default='NO_FILE_SELECTED', help='Image file as a string')
args = ap.parse_args()
image_text = args.f
image = Image.open(image_text)
my_dpi=200.

# Set up figure
fig=plt.figure(figsize=(float(image.size[0])/my_dpi,float(image.size[1])/my_dpi),dpi=my_dpi)
ax=fig.add_subplot(111)

# Remove whitespace from around the image
fig.subplots_adjust(left=0,right=1,bottom=0,top=1)

yInterval = 40.
xInterval = 60.
yloc = plticker.MultipleLocator(base=xInterval)
xloc = plticker.MultipleLocator(base=yInterval)

ax.xaxis.set_major_locator(yloc)
ax.yaxis.set_major_locator(xloc)

ax.grid(which='major', axis='both', linestyle='-')

ax.imshow(image)

# Find number of gridsquares in x and y direction
nx=abs(int(float(ax.get_xlim()[1]-ax.get_xlim()[0])/float(xInterval)))
ny=abs(int(float(ax.get_ylim()[1]-ax.get_ylim()[0])/float(yInterval)))

print nx, ny

# Add some labels to the gridsquares
for j in range(ny):
    y=yInterval/2.+j*yInterval
    for i in range(nx):
        x=xInterval/2.+float(i)*xInterval
        ax.text(x,y,'({:d},{:d})'.format(j,i),color='w',ha='center',va='center', size=5)

# Save the figure
split = image_text.split('/')
outfile = split[len(split) - 1] + '_tiled.png'
fig.savefig(outfile,dpi=my_dpi)