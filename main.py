from ffpyplayer.player import MediaPlayer
import pygame
import cv2



class Presentation:
    def __init__(self, slides, width, height, fullscreen=False):
        pygame.init()
        self.slides = slides
        self.width = width
        self.height = height

        # Set up the display
        if fullscreen:
            self.window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption('Presentation')

        # Clock for FPS
        self.clock = pygame.time.Clock()

        # video player and audio player variables
        self.video_player = None
        self.audio_player = None
        self.video_loaded = False
        self.video_fps = 0


        # Set current index in slides
        self.index = 0
        self.running = True
        while self.running:
            #handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_LEFT:
                        self.index -= 1
                        self.stop_video()
                    elif event.key == pygame.K_RIGHT:
                        self.index += 1
                        self.stop_video()

            # check if we've reached the end of the presentation
            if self.index >= len(self.slides):
                self.index = 0

            # Clear the screen
            self.window.fill((0, 0, 0))

            # Get index type
            index_type = self.get_index_type(self.index)

            if (self.video_loaded is False) and index_type == "video":
                self.video_player = cv2.VideoCapture(self.slides[self.index])
                self.audio_player = MediaPlayer(self.slides[self.index])
                self.video_player.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.video_fps = int(self.video_player.get(cv2.CAP_PROP_FPS))
                self.video_loaded = True

            if self.video_loaded and index_type == "video":
                ret, video_frame = self.video_player.read()
                audio_frame, val = self.audio_player.get_frame()
                if ret:
                    frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB
                    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    frame, w, h = self.scale_image(frame)
                    self.window.blit(frame, (w, h))
                else:
                    #cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Restarts the video if it ends
                    self.stop_video()
                    self.index += 1
            elif index_type == "image":
                img = pygame.image.load(self.slides[self.index])
                img, w, h = self.scale_image(img)
                self.window.blit(img, (w, h))
            else:
                print("Unknown index type, unsupported file format")

            self.clock.tick(self.video_fps if index_type == "video" else 30)
            pygame.display.flip()

        # Quit Pygame
        pygame.quit()

    def stop_video(self):
        self.video_loaded = False
        if self.video_player is not None:
            self.video_player.release()
            self.video_player = None
        if self.audio_player is not None:
            self.audio_player.close_player()
            self.audio_player = None
        self.video_fps = 0
    def scale_image(self, img: pygame.image):
        iw, ih = img.get_size()
        ww, wh = self.window.get_size()
        rw = ww / iw
        rh = wh / ih
        if rw > rh:
            new_width = int(iw * rh)
            return pygame.transform.smoothscale(img, (new_width, wh)), abs(new_width - ww) // 2, 0
        elif rh > rw:
            new_height = int(ih * rw)
            return pygame.transform.smoothscale(img, (ww, new_height)), 0, abs(new_height - wh) // 2
        else:
            return pygame.transform.smoothscale(img, (ww, wh)), 0, 0

    def get_index_type(self, index):
        file_ext = self.slides[index][slides[index].rfind("."):]
        if file_ext == ".mkv":
            return "video"
        elif file_ext in (".png", ".jpg"):
            return "image"
        else:
            return None


if __name__ == '__main__':
    slides = ["example_presentation/slide1.png", "example_presentation/slide2.jpg", "example_presentation/slide3.jpg", "example_presentation/slide4.mkv", "example_presentation/slide5.png"]
    Presentation(slides, 1920, 1080, fullscreen=False)
