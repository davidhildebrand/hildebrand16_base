#!/usr/bin/python
__author__ = 'David Grant Colburn Hildebrand'

import argparse
import math
import numpy
import os
from PIL import Image


def directory(path):
    if not os.path.isdir(path):
        err_msg = "path is not a directory (%s)"
        raise argparse.ArgumentTypeError(err_msg)
    return path


# parse command line options
parser = argparse.ArgumentParser()
parser.add_argument(
    '-p', '--path', type=directory, required=True,
    help="Path to a directory containing a subdirectory corresponding" \
         "to the section number that contains 0-scale PNG tiles in CATMAID" \
         "tile source format 4 (section/scale/row_col.png). [required]")
parser.add_argument(
    '-z', '--sect', type=int, required=True,
    help="Index associated with the section for which >0-scale pyramid" \
         "tiles are to be generated. [required]")
parser.add_argument(
    '-v', '--verbose', action='store_true',
    help="Verbose output. [optional]" )
opts = parser.parse_args()


trans_intens = 255
#background = 250


path = opts.path
sect = opts.sect
verb = opts.verbose
sect_path = os.path.join(path, str(sect))
s0_path = os.path.join(sect_path, '0')
ext = '.png'

# automatically determine tile information
#   and montage width (cols) and height (rows)
s0_tiles = [ f for f in os.listdir(s0_path) if os.path.isfile(os.path.join(s0_path, f)) \
                                            and os.path.splitext(f)[1].lower() == ext ]

# automatically detect tile size
s0_tile = Image.open(os.path.join(s0_path, s0_tiles[0]))
if s0_tile.size[0] == s0_tile.size[1]:
    tile_size = s0_tile.size[0]
else:
    print "ERROR: 0-scale tiles are not square"
    exit()
tile_mode = s0_tile.mode
tile_info = s0_tile.info
if tile_mode != 'L':
    print "ERROR: support currently exists for luminance mode"
    exit()

s0_rows = max([ int(os.path.splitext(f)[0].split('_')[0]) for f in s0_tiles ]) + 1
s0_cols = max([ int(os.path.splitext(f)[0].split('_')[1]) for f in s0_tiles ]) + 1
s0_height = s0_rows * tile_size 
s0_width = s0_cols * tile_size

if len(s0_tiles) != (s0_rows * s0_cols):
    print "ERROR: expected number of 0-scale tiles not found" \
          "       ... expected " + str(s0_rows * s0_cols) + " but found " + len(s0_tiles)
    exit()

print "scale 0"
print "    path " + s0_path
print "    w" + str(s0_width) + "px x h" + str(s0_height) + "px"

# allocate empty tile in case tiles do not exist or cannot be opened
empty_tile = Image.new(tile_mode, (tile_size, tile_size))
empty_tile.paste(trans_intens, (0, 0, tile_size, tile_size))

# set initial 1-scale parameters
scale = 1
height = math.ceil(s0_height / 2)
width = math.ceil(s0_width / 2)

while height >= math.ceil(tile_size / 2) and width >= math.ceil(tile_size / 2): 
    print "  scale " + str(scale)
    scale_path = os.path.join(sect_path, str(scale))
    if not os.path.isdir(scale_path):
        print "    path not found"
        print "      created directory " + scale_path
        os.makedirs(scale_path, 0755)

    print "    path " + scale_path
    print "    w" + str(width) + "px x h" + str(height) + "px"

    # initialize for this scale
    top = 0
    left = 0
    # determine number of rows/cols for this scale
    rows = range(int(math.ceil(height / tile_size)))
    cols = range(int(math.ceil(width / tile_size)))
    print "    rows " + str(len(rows)) + " cols " + str(len(cols))
    for row in rows:
        top = row * tile_size
        for col in cols:
            left = col * tile_size

            # open tiles for previous scale
            try:
                tl_path = os.path.join(sect_path, str(scale - 1), \
                                       str(2 * row) + "_" + str(2 * col) + ext)
                if verb:
                    print "tl_path" + tl_path
                tl = Image.open(tl_path)
                tl_info = tl.info
                # clip if no existing tRNS flag set in the tile info
                if not 'transparency' in tl_info.keys():
                    tl_arr = numpy.array(tl)
                    tl_arr = numpy.clip(tl_arr, 0, trans_intens - 1)
                    tl_data = Image.fromarray(tl_arr)
                else:
                    tl_data = tl
            except IOError:
                print "        WARNING: could not open (" + \
                      os.path.join(str(scale - 1), \
                                   str(2 * row) + "_" + str(2 * col) + ext) + \
                      ")... replaced with empty tile"
                tl_data = Image.new(tile_mode, (tile_size, tile_size))
                tl_data.paste(empty_tile)

            try:
                tr_path = os.path.join(sect_path, str(scale - 1), \
                                       str(2 * row) + "_" + str((2 * col) + 1) + ext)
                if verb:
                    print "tr_path" + tr_path
                tr = Image.open(tr_path)
                tr_info = tr.info
                # clip if no existing tRNS flag set in the tile info
                if not 'transparency' in tr_info.keys():
                    tr_arr = numpy.array(tr)
                    tr_arr = numpy.clip(tr_arr, 0, trans_intens - 1)
                    tr_data = Image.fromarray(tr_arr)
                else:
                    tr_data = tr
            except IOError:
                print "        WARNING: could not open (" + \
                      os.path.join(str(scale - 1), \
                                   str(2 * row) + "_" + str((2 * col) + 1) + ext) + \
                      ")... replaced with empty tile"
                tr_data = Image.new(tile_mode, (tile_size, tile_size))
                tr_data.paste(empty_tile)

            try:
                bl_path = os.path.join(sect_path, str(scale - 1), \
                                       str((2 * row) + 1) + "_" + str(2 * col) + ext)
                if verb:
                    print "bl_path" + bl_path
                bl = Image.open(bl_path)
                bl_info = bl.info
                # clip if no existing tRNS flag set in the tile info
                if not 'transparency' in bl_info.keys():
                    bl_arr = numpy.array(bl)
                    bl_arr = numpy.clip(bl_arr, 0, trans_intens - 1)
                    bl_data = Image.fromarray(bl_arr)
                else:
                    bl_data = bl
            except IOError:
                print "        WARNING: could not open (" + \
                      os.path.join(str(scale - 1), \
                                   str((2 * row) + 1) + "_" + str(2 * col) + ext) + \
                      ")... replaced with empty tile"
                bl_data = Image.new(tile_mode, (tile_size, tile_size))
                bl_data.paste(empty_tile)

            try:
                br_path = os.path.join(sect_path, str(scale - 1), \
                                       str((2 * row) + 1) + "_" + str((2 * col) + 1) + ext)
                if verb:
                    print "br_path" + br_path
                br = Image.open(br_path)
                br_info = br.info
                # clip if no existing tRNS flag set in the tile info
                if not 'transparency' in br_info.keys():
                    br_arr = numpy.array(br)
                    br_arr = numpy.clip(br_arr, 0, trans_intens - 1)
                    br_data = Image.fromarray(br_arr)
                else:
                    br_data = br
            except IOError:
                print "        WARNING: could not open (" + \
                      os.path.join(str(scale - 1), \
                                   str((2 * row) + 1) + "_" + str((2 * col) + 1) + ext) + \
                      ")... replaced with empty tile"
                br_data = Image.new(tile_mode, (tile_size, tile_size))
                br_data.paste(empty_tile)

            # allocate 2x2 tile array that will be downsampled
            tile = Image.new(tile_mode, (2 * tile_size, 2 * tile_size))

            # copy opened tiles into 2x2 tile array
            tile.paste(tl_data, (0, 0))
            tile.paste(tr_data, (tile_size, 0))
            tile.paste(bl_data, (0, tile_size))
            tile.paste(br_data, (tile_size, tile_size))

            # downsample 2x2 tile array to single tile
            #  it would be nice to use Image.ANTIALIAS or Image.BICUBIC,
            #  but these make it more likely that the tRNS value will be hit
            #  ... which leads to unwanted transparency
            tile = tile.resize((tile_size, tile_size), Image.BILINEAR)
            
            # preserve tile info and force tRNS alpha value
            if not 'transparency' in tile_info.keys():
                # set the tRNS flag to intensity value trans_intens in the image info
                tile_info['transparency'] = trans_intens
            tile.info = tile_info

            # save new tile
            save_path = os.path.join(sect_path, str(scale), \
                                     str(row) + "_" + str(col) + ext)
            tile.save(save_path, **tile_info)
            print "      row " + str(row) + " col " + str(col) + \
                  " (top " + str(top) + " left " + str(left) + ") saved"

    # set up next iteration
    scale += 1
    height = math.ceil(height / 2)
    width = math.ceil(width / 2)

