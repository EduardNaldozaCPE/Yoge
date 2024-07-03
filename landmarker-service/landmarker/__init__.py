# USAGE:

#   # 1. import modules
# 
#     import Landmarker
#     import threading
# 

#   # 2. Instantiate the service
# 
#     service = Landmarker()
#

#   # 3. Set the session data at top level
#   # (This creates a new record in yoge.session)
# 
#     service.setSessionData()
#   

#   # 4. Create a separate thread for runVideo loop
# 
#     video_thread = threading.Thread(target=poseEstimationService.runVideo)
#     video_thread.start()
# 

#   # 5. Get the last frame data using Landmarker.getFrameData()
#     frame_data = service.getFrameData()
from .Landmarker import Landmarker