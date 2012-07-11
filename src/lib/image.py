'''
Created on Mar 13, 2012

Image processing helpers

@author: Benjamin Dezile
'''

from PIL import Image

class KImage:
    ''' Image processing wrapper '''
    
    THUMB_IMAGE_DIMS = (75, 75)             # Dimensions of thumbnail images
    MAX_IMAGE_DIMS = (1024, 768)            # Large images will be shrunk down to this
    
    def __init__(self, file_path):
        self.path = file_path
        self.img = Image.open(file_path)
    
    @property
    def size(self):
        ''' Return the dimenensions of this image '''
        return self.img.size
    
    def enforce_dimensions(self):
        ''' Resize the image if larger than allowed. 
        Return True if it was resized
        '''
        size = self.img.size
        if size[0] > self.MAX_IMAGE_DIMS[0] or size[1] > self.MAX_IMAGE_DIMS[1]:
            self.img.thumbnail(self.MAX_IMAGE_DIMS, Image.ANTIALIAS)
            self.img.save(self.path) 
            return True
    
    def make_thumbnail(self):
        ''' Generate a thumbnail for this image. 
        Return the path to the thumbnail image file.
        '''
        
        thumb_path = KImage.get_thumbnail_file_path(self.path)
        
        self.img.thumbnail(self.THUMB_IMAGE_DIMS, Image.ANTIALIAS)
        self.img.save(thumb_path)
        
        return thumb_path

    @classmethod        
    def get_thumbnail_file_path(cls, path):
        ''' Return the thumbnail file path for the given image path '''
        p = path.rfind(".")
        path = path[:p] + ".thumb" + path[p:]
        return path
