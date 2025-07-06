class Reference():
    def __init__(self, video_path):
        self.video_path = video_path
        self.frame_count = 0
        self.fps = 0
        self.width = 0
        self.height = 0



class Distorded():
    def __init__(self, video_path):
        self.video_path = video_path
        self.frame_count = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        self.frames = []
        self.ssim_computed = False
        self.psnr_computed = False  
        self.vmaf_computed = False
        self.ssim_values = []
        self.psnr_values = []
        self.vmaf_values = []

    def reset_values(self):
        self.ssim_values = []
        self.psnr_values = []
        self.vmaf_values = []
    
    

reference = Reference("D:\\Untitled.mp4")
distorted = Distorded("D:\\Untitled2.mp4")

