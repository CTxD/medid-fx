import os
import base64
import uuid


class Encoding2TmpFile():
    def __init__(self, encoding: str):
        self.encoding = encoding
        self.tempdir = os.path.join(os.getcwd(), str(uuid.uuid4()))
        self.tempfilepath = os.path.join(self.tempdir, str(uuid.uuid4()) + '.jpg')

    def __enter__(self):
        # Create the tempdir , if it does not exist
        if not os.path.exists(self.tempdir):
            os.mkdir(self.tempdir)
        
        with open(self.tempfilepath, mode='wb') as f:
            f.write(base64.b64decode(self.encoding))
        
        return self.tempfilepath
    
    def __exit__(self, type, value, traceback): # noqa
        # Remove all files in the tempdir
        for f in os.listdir(self.tempdir):
            os.remove(os.path.join(self.tempdir, f))
        
        # Remove the (now empty) tempdir
        os.rmdir(self.tempdir)