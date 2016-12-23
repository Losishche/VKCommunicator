# -*- coding: UTF8 -*-

import urllib, urllib2
import imghdr, hashlib, base64, mimetypes, re, StringIO, sys
import PIL.Image

GRAFFITI_FULL_SIZE_W = 586
GRAFFITI_THUMB_SIZE_W = 272
GRAFFITI_THUMB_SIZE_H = 136

SENDAS_JPEG = 0
SENDAS_PNG = 1
SENDAS_PNG_JPEG = 2

#generic grafiti error
class GraffitiError(Exception):
    def __init__(self, errmsg=u""):
        self.errmsg = errmsg
    
    def __unicode__(self):
        return self.errmsg
    

#unsupported image type
class WrongImageTypeError(GraffitiError):
    pass

#wrong friendID or groupID in PostImage
class WrongPostID(GraffitiError):
    pass

#wrong sendas value in PostImage
class WrongSendAs(GraffitiError):
    pass

#image too big
class ImageTooBig(GraffitiError):
    def __init__(self):
        GraffitiError.__init__(self, u"изображение слишком большое")

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    
    def get_content_type(filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    BOUNDARY = '--OLEG-ANDREEV-PAVEL-DUROV-GRAFFITI-POST'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


class Graffiti:
    def __init__(self, vkontakte_auth):
        self._auth = vkontakte_auth
        self._image_path = ''
        self._image_data_png = ''
        self._image_data_jpeg = ''
        self._image_type = 'unknown'        
        
        self.ALLOWED_TYPES = ['jpeg', 'bmp', 'png']
        
    def LoadImage(self, local_path):        
        f = open(local_path, "rb")        
        img_type = imghdr.what(None, f.read(32))
        if img_type not in self.ALLOWED_TYPES:
            raise WrongImageTypeError()
        
        f.seek(0)
        image = PIL.Image.open(f)
        image.load()        
                
        (w, h) = image.size
        
        if img_type == 'png' and w == GRAFFITI_FULL_SIZE_W:
            # use original image intact
            self._full_image = image
            f.seek(0)
            self._full_image_data_png = f.read();
        else:
            # scale image for full view (if original image not suitable)
            image = image.convert() #convert palleted images to common mode            
            if GRAFFITI_FULL_SIZE_W == w:
                self._full_image = image
            else:
                new_h = int(GRAFFITI_FULL_SIZE_W * h / w)
                if GRAFFITI_FULL_SIZE_W < w:
                    self._full_image = image.resize((GRAFFITI_FULL_SIZE_W, new_h), PIL.Image.ANTIALIAS)
                else:
                    self._full_image = image.resize((GRAFFITI_FULL_SIZE_W, new_h), PIL.Image.BICUBIC)
                    
            stream = StringIO.StringIO()
            self._full_image.save(stream, "PNG", optimize=1)
            self._full_image_data_png = stream.getvalue()
        
        stream = StringIO.StringIO()
        self._full_image.save(stream, "JPEG", optimize=1)
        self._full_image_data_jpeg = stream.getvalue()
        
        #scale it for wall size (in any case)
        if GRAFFITI_THUMB_SIZE_W < w:
            self._wall_image = image.resize((GRAFFITI_THUMB_SIZE_W, GRAFFITI_THUMB_SIZE_H), PIL.Image.ANTIALIAS)
        else:
            self._wall_image = image.resize((GRAFFITI_THUMB_SIZE_W, GRAFFITI_THUMB_SIZE_H), PIL.Image.BICUBIC)
        stream = StringIO.StringIO()
        self._wall_image.save(stream, "PNG")
        self._wall_image_data = stream.getvalue()
        
        self._image_path = local_path
        self._image_type = img_type    #original image type        
        f.close()
        
    def GetImageData(self, sendas):
        if sendas not in [SENDAS_JPEG, SENDAS_PNG]:
            raise WrongSendAs()
        
        if sendas == SENDAS_JPEG:
            return self._full_image_data_jpeg
        else:
            return self._full_image_data_png
    
    def GetWallImageData(self):
        return self._wall_image_data
    
    def GetImageType(self):
        return self._image_type
    
    def GetImagePath(self):
        return self._image_path
    
    def IsReady(self):
        return self._image_type != 'unknown'
        
    #uploads an image and return URL of the page, to which it's uploaded
    #type is 'friend' or 'club'
    def PostImage(self, type, id, sendas):
        print >> sys.stderr, u"Posting graffiti..."
        if type not in ['friend', 'group']:
            raise WrongPostID()
        
        if sendas not in [SENDAS_JPEG, SENDAS_PNG, SENDAS_PNG_JPEG]:
            raise WrongSendAs()        
        
        to_id = 0;
        to_group = 0;
        
        if type == 'friend':
            to_id = int(id)
            
        if type == 'group':
            to_group = int(id)
            
        if sendas == SENDAS_JPEG:
            return (self._try_upload(to_id, to_group, self._full_image_data_jpeg), SENDAS_JPEG)
        elif sendas == SENDAS_PNG:
            return (self._try_upload(to_id, to_group, self._full_image_data_png), SENDAS_PNG)
        
        #try png first, jpeg on ImageToBig
        try:
            return (self._try_upload(to_id, to_group, self._full_image_data_png), SENDAS_PNG)
        except ImageTooBig, e:
            return (self._try_upload(to_id, to_group, self._full_image_data_jpeg), SENDAS_JPEG)
        
    
    def _try_upload(self, to_id, to_group, image_data):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self._auth.get_cookie()))
        
        image_hash = hashlib.md5(base64.encodestring(image_data).replace('\n','')[:1024]).hexdigest()        
        
        post_fields = [('Signature', image_hash), ('Upload', 'Submit Query')]
        post_files = [('Filedata', 'graffiti.png', image_data)]
        (content_type, post_body) = encode_multipart_formdata(post_fields, post_files)
        
        query = "http://vkontakte.ru/graffiti.php?to_id=%d&group_id=%d" % (to_id, to_group)
        request = urllib2.Request(query)
        request.add_header('Referer', 'http://vkontakte.ru/swf/Graffiti.swf?15')
        request.add_header('Content-Type', content_type)
        request.add_data(post_body)

        print >> sys.stderr, u"uploading,"
        try:
            response = opener.open(request)
        except urllib2.HTTPError, e:
            if e.code == 413:
                raise ImageTooBig()
            else:
                raise
        
        #get post_hash
        #post hash must be obtained from target wall
        if to_id != 0:
            target_url = "http://vkontakte.ru/id%d" % to_id
        else:
            target_url = "http://vkontakte.ru/club%d" % to_group

        response = opener.open(target_url)
        data = response.read()
        hash_match = re.findall(r'"post_hash":"(.+?)"', data)
        if len(hash_match) == 0:
            raise GraffitiError(u"не найден хэш сообщения")
        post_hash = hash_match[0]
        print >> sys.stderr, "post_hash is %s" % post_hash


        #get media id
        post = urllib.urlencode({'act': 'last_graffiti', 'al': '1'})
        request = urllib2.Request("http://vkontakte.ru/al_wall.php", post)
        response = opener.open(request)
        data = response.read()
        media_match = re.findall(r'.*?<!>.*?<!>.*?<!>.*?<!>.*?<!>(\d+_\d+)<!>', data)
        if len(media_match) == 0:
            raise GraffitiError(u"не найден идентификатор граффити")
        media_id = media_match[0]
        print >> sys.stderr, "media is %s" % media_id
        
        #confirm graffiti
        #Yeah! This is possible again!
        if to_id == 0:
            to_id = -to_group

        post = urllib.urlencode({'act': 'post',
                                 'al': '1', 
                                 'hash': post_hash,
                                 'media': media_id,
                                 'media_type': 'graffiti',
                                 'to_id': str(to_id),
                                 'type': 'all'});
        request = urllib2.Request("http://vkontakte.ru/al_wall.php", post)
        response = opener.open(request)

        print >> sys.stderr, u"done."

        return target_url
        
