from uttt_data import *
from pygame_game import PygameGame
import pygame, pygame.locals
import uttt_data

class UTTTGame(PygameGame):

    def __init__(self, width_px, height_px, frames_per_second, data, send_queue):
        # PygameGame sets self.width and self.height        
        PygameGame.__init__(self, "Ultimate Tic Tac Toe", width_px, height_px, frames_per_second)
        self.data = data
        self.send_queue = send_queue
        return

    def handle_state(self):
        if self.data:
            state = self.data.GetState()
            if state in [ uttt_data.STATE_SHOW_SIGNUP, uttt_data.STATE_WAIT_SIGNUP, 
                          uttt_data.STATE_SIGNUP_FAIL_USERNAME,
                          uttt_data.STATE_SHOW_LOGIN, uttt_data.STATE_WAIT_LOGIN, uttt_data.STATE_LOGIN_FAIL,
                          uttt_data.STATE_SIGNUP_FAIL_EMAIL, uttt_data.STATE_SIGNUP_FAIL_PASSWORD,
                          uttt_data.STATE_SIGNUP_FAIL_PASSWORD_UNMATCHED, uttt_data.STATE_SIGNUP_OK ]:
                # minimize window
                #pygame.display.iconify()
                if self.screen.get_size() != ( 1, 1 ):
                    print "shrink"
                    self.screen = pygame.display.set_mode(
                        # set the size
                        (1, 1),
                        # use double-buffering for smooth animation
                        pygame.DOUBLEBUF |
                        # apply alpha blending
                        pygame.SRCALPHA |
                        # allow resizing
                        pygame.RESIZABLE)
                
            elif state in [ uttt_data.STATE_WAIT_GAME, uttt_data.STATE_SHOW_GAME,
                            uttt_data.STATE_GAME_OVER, uttt_data.STATE_TURN_FAILED,
                            uttt_data.STATE_WAIT_TURN ]:
                # unminimize window
                if self.screen.get_size() != ( self.width, self.height ):
                    print "WHAT?  pygame doesn't support unminimize?"
                    self.screen = pygame.display.set_mode(
                        # set the size
                        (self.width, self.height),
                        # use double-buffering for smooth animation
                        pygame.DOUBLEBUF |
                        # apply alpha blending
                        pygame.SRCALPHA |
                        # allow resizing
                        pygame.RESIZABLE)
            elif state in [ uttt_data.STATE_SOCKET_CLOSED, uttt_data.STATE_SOCKET_ERROR,
                            uttt_data.STATE_ERROR ]:
                # close
                print "Socket closed, or other error, pygame will quit."
                pygame.quit()
            elif state in [ uttt_data.STATE_SOCKET_OPEN ]:
                # what should I do?
                pass
            else:
                print "Unknown state in pygame: ", state

        return

    def game_logic(self, keys, newkeys, buttons, newbuttons, mouse_position):
        self.handle_state()
        
        if 1 in newbuttons:
            if self.data.GetNextPlayer() != self.data.GetPlayer():
                # not our turn
                return

            mX,mY = mouse_position[0], mouse_position[1]
            col = mX / (self.width/9)
            row = mY / (self.height/9)
            board = 3 * (row / 3) + (col / 3)
            position = 3 * (row % 3) + (col % 3)
            
            if self.data and self.send_queue:
                text = self.data.SendTurn(board, position)
                print "pygame: queuing: %s" % (text, )
                self.send_queue.put(text)
        return

    def paint(self, surface):
        # Background
        rect = pygame.Rect(0,0,self.width,self.height)
        surface.fill((0,0,0),rect )
        
        # Regular Lines
        for i in range(1,9):
            pygame.draw.line(surface, (255,255,255), (0, i*self.height/9), (self.width, i*self.height/9))
        for j in range(1,9):
            pygame.draw.line(surface, (255,255,255), (j*self.width/9, 0), (j*self.height/9, self.height))

        # Board Lines
        for k in range(1,3):
            pygame.draw.line(surface, (255,255,0), (0, k*self.height/3), (self.width, k*self.height/3), 3)
        for l in range(1,3):
            pygame.draw.line(surface, (255,255,0), (l*self.width/3, 0), (l*self.height/3, self.height), 3)

        # Markers
        for board in range(9):
            for position in range(9):
                col = 3 * (board % 3) + position % 3
                row = 3 * (board / 3) + position / 3
                x = int((col + .5) * self.width / 9)
                y = int((row + .5) * self.height / 9)
                marker = self.data.GetMarker(board, position)
                if marker == uttt_data.PLAYER_X:
                    pygame.draw.circle(surface, (0,0,255), (x, y), 5)
                elif marker == uttt_data.PLAYER_O:
                    pygame.draw.circle(surface, (255,0,0), (x, y), 5)
        return

def uttt_pygame_main(data, send_queue):
    game = UTTTGame(600, 600, 30, data, send_queue)
    game.main_loop()
    return

if __name__ == "__main__":
    uttt_pygame_main(UTTTData(), None)
