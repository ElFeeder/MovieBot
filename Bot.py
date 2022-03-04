from google_images_download import google_images_download
  
  
def downloadimages(query):
    # keywords is the 
    # format is the 
    # limit is the 
    # print urs is to 
    # size is the  which can
    # be specified manually 
    # aspect ratio denotes the height width ratio
    # of images to download. 
    arguments = {"keywords":    query,   # Search query
                 "format":      "jpg",      # Image file format
                 "limit":       4,          # Number of images to be downloaded
                 "print_urls":  False,      # Print the image file url
                 "size":        "medium"}   # Image size ("large, medium, icon")
                                            # Aspect ratio ("tall, square, wide, panoramic")
    
    try:
        response.download(arguments)
    except:
        print("Couldn't find anything.")
        pass

# Object to hold response from API
response = google_images_download.googleimagesdownload() 
  
searchQueries = ['Shrek']

# Driver Code
for query in searchQueries:
    downloadimages(query) 
    print() 