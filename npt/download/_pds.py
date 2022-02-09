from npt.utils import filenames

def split_label_from_image(img_filename):
    """
    Write PDS Label content from image with '.LBL' extension
    """
    label = read_image_header(img_filename)
    lbl_filename = filenames.change_extension(img_filename, 'lbl')
    with open(lbl_filename, 'w') as fp:
        fp.write(label.read())

    print("PDS LABEL file '{}' created.".format(lbl_filename))
    return lbl_filename


def read_image_header(img_filename):
    """
    Return PDS LABEL (text) from PDS IMAGE
    """
    import io
    header = io.StringIO()
    with open(img_filename, 'r') as fp:
        try:
            for line in fp:
                if '\x00' in line:
                    break
                else:
                    header.write(line)
        except:
            pass

    header.seek(0)
    return header


def write_feature_json(feature:dict, image_path:str='image_path') -> bool:
    """
    Write feature/metadata next to feature['image_path']
    """
    import json
    try:
        json_filename = filenames.change_extension(feature['properties'][image_path], 'json')
        with open(json_filename, 'w') as fp:
            json.dump(feature, fp)
        return json_filename
    except Exception as err:
        raise err
        return None
