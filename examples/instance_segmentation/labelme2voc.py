#!/usr/bin/env python

from __future__ import print_function

import argparse
import glob
import json
import os
import os.path as osp

import numpy as np
import PIL.Image

import labelme


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('labels_file')
    parser.add_argument('in_dir')
    parser.add_argument('out_dir')
    args = parser.parse_args()

    if osp.exists(args.out_dir):
        print('Output directory already exists:', args.out_dir)
        quit(1)
    os.makedirs(args.out_dir)
    os.makedirs(osp.join(args.out_dir, 'JPEGImages'))
    os.makedirs(osp.join(args.out_dir, 'SegmentationClass'))
    os.makedirs(osp.join(args.out_dir, 'SegmentationClassVisualization'))
    os.makedirs(osp.join(args.out_dir, 'SegmentationObject'))
    os.makedirs(osp.join(args.out_dir, 'SegmentationObjectVisualization'))
    print('Creating dataset:', args.out_dir)

    class_names = []
    class_name_to_id = {}
    for i, line in enumerate(open(args.labels_file).readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        class_name_to_id[class_name] = class_id
        if class_id == -1:
            assert class_name == '__ignore__'
            continue
        elif class_id == 0:
            assert class_name == '_background_'
        class_names.append(class_name)
    class_names = tuple(class_names)
    print('class_names:', class_names)
    out_class_names_file = osp.join(args.out_dir, 'class_names.txt')
    with open(out_class_names_file, 'w') as f:
        f.writelines('\n'.join(class_names))
    print('Saved class_names:', out_class_names_file)

    colormap = labelme.utils.label_colormap(255)

    for label_file in glob.glob(osp.join(args.in_dir, '*.json')):
        print('Generating dataset from:', label_file)
        with open(label_file) as f:
            base = osp.splitext(osp.basename(label_file))[0]
            out_img_file = osp.join(
                args.out_dir, 'JPEGImages', base + '.jpg')
            out_cls_file = osp.join(
                args.out_dir, 'SegmentationClass', base + '.png')
            out_clsv_file = osp.join(
                args.out_dir, 'SegmentationClassVisualization', base + '.jpg')
            out_ins_file = osp.join(
                args.out_dir, 'SegmentationObject', base + '.png')
            out_insv_file = osp.join(
                args.out_dir, 'SegmentationObjectVisualization', base + '.jpg')

            data = json.load(f)

            img_file = osp.join(osp.dirname(label_file), data['imagePath'])
            img = np.asarray(PIL.Image.open(img_file))
            PIL.Image.fromarray(img).save(out_img_file)

            cls, ins = labelme.utils.shapes_to_label(
                img_shape=img.shape,
                shapes=data['shapes'],
                label_name_to_value=class_name_to_id,
                type='instance',
            )

            PIL.Image.fromarray(cls).save(out_cls_file)
            label_names = ['%d: %s' % (cls_id, cls_name)
                           for cls_id, cls_name in enumerate(class_names)]
            clsv = labelme.utils.draw_label(
                cls, img, label_names, colormap=colormap)
            PIL.Image.fromarray(clsv).save(out_clsv_file)

            PIL.Image.fromarray(ins).save(out_ins_file)
            instance_ids = np.unique(ins)
            instance_names = [str(i) for i in range(max(instance_ids) + 1)]
            insv = labelme.utils.draw_label(
                ins, img, instance_names)
            PIL.Image.fromarray(insv).save(out_insv_file)


if __name__ == '__main__':
    main()
