from npt.utils import filenames
from npt.utils import geojson

write_feature_json = geojson.write_feature_json

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
