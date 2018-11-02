import base64

###ENCODE THE IMAGE IN BASE-64####

image = open('download.jpeg','rb')
image_read = image.read()
image_64_encode = base64.encodestring(image_read)
#print(image_64_encode)

### TO DECOCE THE ENCODED IMAGE###

image_64_decode = base64.decodestring(image_64_encode)
image_result = open('decoded.jpeg','wb')
image_result.write(image_64_decode)
