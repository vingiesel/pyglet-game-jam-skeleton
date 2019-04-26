import math

from pyglet.gl import *

class Image(object):
    """A an image object."""
    #def __init__(self, ID, quad, w, h):
    #    self.id = ID
    #    self.quad = quad
    #    self.rx = w
    #    self.ry = h

class Text(object):
    """A Text object."""
    def __init__(self):
        self.id = -1
        self.text = ""
        self.imr = pygame.Rect(0,0,0,0)
        self.rx = 0
        self.ry = 0
        self.quad = -1
    def SetText(self, text, font):
        if text == self.text:
            return
        self.text = text

        d = font.render(text, 0, (255,255,255))
        
        r = d.get_rect()
        self.imr = r

        p2w = 2 ** int(math.ceil(math.log(self.imr.w) / math.log(2)))
        p2h = 2 ** int(math.ceil(math.log(self.imr.h) / math.log(2)))

        tcx = self.imr.w/float(p2w)
        tcy = self.imr.h/float(p2h)

        data = pygame.Surface((p2w,p2h), SRCALPHA)
        data.blit(d, (0,0))

        #Set as an image
        textureData = pygame.image.tostring(data, "RGBA")
        tex = 0
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, data.get_width(), data.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData);
        #glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, im->w,                     im->h,                       0, GL_BGRA, GL_UNSIGNED_BYTE, im->pixels);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        self.ry = 1.0
        self.rx = (float(self.imr.w)/float(self.imr.h))


        self.quad = glGenLists(1)
        glNewList(self.quad,GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, tex)
        glBegin(GL_QUADS)
        
        glTexCoord2f(0,0)
        glVertex3f(-0.5, -0.5, 0)

        glTexCoord2f(tcx,0)
        glVertex3f(0.5, -0.5, 0)

        glTexCoord2f(tcx,tcy)
        glVertex3f(0.5, 0.5, 0)

        glTexCoord2f(0,tcy)
        glVertex3f(-0.5, 0.5, 0)
        
        glEnd()
        glEndList()

        self.id = tex


class Viewport(object):
    """A viewport contains information about the viewing area."""
    def __init__(self, x,y,w,h, resx,resy):
        """Init.Parameters:

        (x,y): where the viewport is on the screen ( (0,0) is the top-left corner, (1,1) is the bottom-right).
        
        (w,h): how much space it takes up on the screen.
        
        (resx,resy): its dimensions in openGL units."""
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.resx = resx
        self.resy = resy

class Engine(object):
    """
    The main Class. An Engine object contains most of the funtionality of the engine.
    """
    def __init__(self, w, h, depth, fullscreen, caption, font = None):
        """
        Initializes the engine.
        Parameters:
            w,h: screen width/height.
            depth: bits per pixel.
            fullscreen: if true, the window is fullscreen.
            caption: the windows caption.
            font: the pygame font the engine should use. if None, the default is loaded.
        """
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.ratio_x = w
        self.ratio_y = h
        self.screen_w = w
        self.screen_h = h
        self.ticks= pygame.time.get_ticks()
        self.camx = 0.0
        self.camy = 0.0
        self.zoom = 1.0
        self.hud_mode = False
        self.loop = 0
        self.quad_v = [
                    -0.5, -0.5,
                    0.5, -0.5,
                    0.5, 0.5,
                    -0.5, 0.5]
        self.quad_v_gl = (GLfloat * len(self.quad_v))(*self.quad_v)

        self.quad_uvs = [0,0, 1,0, 1,1, 0,1]
        self.quad_uvs_gl = (GLfloat * len(self.quad_uvs))(*self.quad_uvs)

        if fullscreen:
            self.screen = pygame.display.set_mode((w, h), OPENGL | DOUBLEBUF | FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((w, h), OPENGL | DOUBLEBUF)
            
        pygame.display.set_caption(caption)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_ALPHA_TEST)

        self.face = glGenLists(1)
        glNewList(self.face,GL_COMPILE)
        glBegin(GL_QUADS)
        
        glTexCoord2f(0,0)
        glVertex3f(-0.5, -0.5, 0)

        glTexCoord2f(1,0)
        glVertex3f(0.5, -0.5, 0)

        glTexCoord2f(1,1)
        glVertex3f(0.5, 0.5, 0)

        glTexCoord2f(0,1)
        glVertex3f(-0.5, 0.5, 0)
        
        glEnd()
        glEndList()

        if font == None:
            self.font = pygame.font.Font("freesansbold.ttf", 80)
        else:
            self.font = font
        self.text = self.Text("", self.font)


        #set the default viewport
        glMatrixMode( GL_PROJECTION );
        glLoadIdentity();
        glOrtho( (-w/2), (w/2), (h/2), (-h/2), -100, 100 );

        glMatrixMode( GL_MODELVIEW );

        glLoadIdentity();
        gluLookAt(0,0,20, 0,0,0, 0,1,0);

        
    def LoadImageData(self,path):
        """
        Loads a pygame.Surface from path.
        """
        textureSurface = pygame.image.load(path)
        # textureSurface = textureSurface.convert_alpha()
        # textureSurface.set_colorkey((255,0,255), pygame.RLEACCEL)
        return textureSurface
    
    def MakeDataFromImage(self,image):
        """
        NOT IMPLEMENTED! I never found any use for it.
        """
        pass
    def LoadSequence(self,path,rows,colunms,total,width, height):
        """
        Splits an image into a list of images.
        """
        image_map = self.LoadImageData(path)
        
        seq = []
        cnt = 0
        
        for r in range(rows):
            for c in range(colunms):
                if cnt >= total:
                    break
                new_image = image_map.subsurface((c*width,r*height,width,height)).copy().convert_alpha()
                
                #new_image = pygame.Surface((width,height), SRCALPHA)
                #new_image.fill((0,0,0,0))
                #new_image.blit(image_map, (0,0,0,0), (c*width,r*height,width,height))
                tex = self.MakeImageFromData(new_image)

                seq.append(tex)
                
                cnt+=1

        return seq

                

                
    def LoadImage(self,path):
        """
        Loads an image from path. Returns a Image object.
        """
        d = self.LoadImageData(path)
        
        r = d.get_rect()
        imr = r

        p2w = 2 ** int(math.ceil(math.log(imr.w) / math.log(2)))
        p2h = 2 ** int(math.ceil(math.log(imr.h) / math.log(2)))

        tcx = imr.w/float(p2w)
        tcy = imr.h/float(p2h)

        rx = 1.0
        ry = (float(imr.h)/float(imr.w))

        data = pygame.Surface((p2w,p2h), SRCALPHA)
        data.blit(d, (0,0))

        textureData = pygame.image.tostring(data, "RGBA")
        tex = 0
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, data.get_width(), data.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData);
        #glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, im->w,                     im->h,                       0, GL_BGRA, GL_UNSIGNED_BYTE, im->pixels);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


        quad = glGenLists(1)
        glNewList(quad,GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, tex)
        glBegin(GL_QUADS)
        
        glTexCoord2f(0,0)
        glVertex3f(-0.5, -0.5, 0)

        glTexCoord2f(tcx,0)
        glVertex3f(0.5, -0.5, 0)

        glTexCoord2f(tcx,tcy)
        glVertex3f(0.5, 0.5, 0)

        glTexCoord2f(0,tcy)
        glVertex3f(-0.5, 0.5, 0)
        
        glEnd()
        glEndList()

        new_image = Image()
        new_image.id = tex
        new_image.quad = quad
        new_image.rx = rx
        new_image.ry = ry

        return new_image

    def MakeImageFromData(self,data):
        """
        Makes an image out of the pygame.Surface data
        """
        

        r = data.get_rect()
        imr = r

        p2w = 2 ** int(math.ceil(math.log(imr.w) / math.log(2)))
        p2h = 2 ** int(math.ceil(math.log(imr.h) / math.log(2)))

        tcx = imr.w/float(p2w)
        tcy = imr.h/float(p2h)

        rx = 1.0
            ry = (float(imr.h)/float(imr.w))

        dat = pygame.Surface((p2w,p2h), SRCALPHA)
        dat.blit(data, (0,0))

        textureData = pygame.image.tostring(dat, "RGBA")
        tex = 0
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, dat.get_width(), dat.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


        quad = glGenLists(1)
        glNewList(quad,GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, tex)
        glBegin(GL_QUADS)
        
        glTexCoord2f(0,0)
        glVertex3f(-0.5, -0.5, 0)

        glTexCoord2f(tcx,0)
        glVertex3f(0.5, -0.5, 0)

        glTexCoord2f(tcx,tcy)
        glVertex3f(0.5, 0.5, 0)

        glTexCoord2f(0,tcy)
        glVertex3f(-0.5, 0.5, 0)
        
        glEnd()
        glEndList()

        new_image = Image()
        new_image.id = tex
        new_image.quad = quad
        new_image.rx = rx
        new_image.ry = ry

        return new_image

    


    def Text(self, string, font):
        """
        Returns a text object, with text set to string. if font is None,
        the engine's default font is used.
        """
        text_obj = Text()
        if font == None:
            self.SetTextString(text_obj, string, self.font)
        else:
            self.SetTextString(text_obj, string, font)
        return text_obj
    def SetTextString(self, text_obj, string, font):
        """
        Sets text_object's text to string, with font as its font.
        """
        if font == None:
            text_obj.SetText(string, self.font)
        else:
            text_obj.SetText(string, font)

    def DrawText(self,text, x,y,scale_x,scale_y,a=1.0, rot=0.0, r=1.0, g=1.0, b = 1.0, UseRatio = True, z = 0):
        """Draw a Text object to the screen.

        Parameters:

            text: the Text object.
            
            x,y:   position.
        
            scale_x,scale_y: Scales the text accordingly.
        
            a:     transperency.
        
            rot:   angle/rotation.

            r,g,b: text the image with this color.
        
            UseRatio:
                if True(default), than the text will be drawn with its
                original proportions. for example, if the text is 64x480, and
                (scale_x,scale_y) set to (10,10), it will show up as 10x20.
                if False, the text will have the exact dimensions set in (scale_x,scale_y).
            z: Depth. keep it between 100 and -100.
        """
        glPushMatrix();

        glTranslatef( x, y, z );

        glRotatef(rot,0,0,1);

        glColor4f(r,g,b,a)

        glScalef(text.rx*scale_x,text.ry*scale_y,1);

        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_EQUAL, 1.0)  
        glDepthMask(GL_TRUE)        
        glCallList(text.quad)
        glAlphaFunc(GL_LESS,1.0)
        glDepthMask(GL_FALSE)   
        glCallList(text.quad)
        glDisable(GL_ALPHA_TEST)
        glDepthMask(GL_TRUE)

        glPopMatrix();

    def DrawString(self, string, x,y, scale_x,scale_y, a = 1.0, rot=0, r = 1.0, g = 1.0, b = 1.0, font = None, z = 0):
        """Draws a string to the screen.

        Parameters:

            string: the text to draw.
            
            x,y:   position.
        
            scale_x,scale_y: Scales the text accordingly.
        
            a:     transperency.
        
            rot:   angle/rotation.

            r,g,b: the text color.

            font: the pygame font to use. The engine default will be used if font=None.
            
            z: Depth. keep it between 100 and -100.
        """
        if font != None:
            self.text.SetText(string, font)
        else:
            self.text.SetText(string, self.font)

        glPushMatrix();

        glTranslatef( x, y, z );

        glRotatef(rot,0,0,1);

        glColor4f(r,g,b,a)

        glScalef(self.text.rx*scale_x,self.text.ry*scale_y,1);

        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_EQUAL, 1.0)  
        glDepthMask(GL_TRUE)        
        glCallList(self.text.quad)
        glAlphaFunc(GL_LESS,1.0)
        glDepthMask(GL_FALSE)   
        glCallList(self.text.quad)
        glDisable(GL_ALPHA_TEST)
        glDepthMask(GL_TRUE)
        
        glPopMatrix();

    def DrawImage(self,image, x,y,w,h,a,rot,r=1.0,g=1.0,b=1.0,UseRatio = True, Cull = False, z = 0):
        """Draw an Image object to the screen.

        Parameters:
        
            image: the Image object.
            
            x,y:   position.
        
            w,h:   dimensions.
        
            a:     transperency.
        
            rot:   angle/rotation.

            r,g,b: tints the image with this color.
        
            UseRatio:
                if True(default), than the image will be drawn with its
                original proportions. for example, if a 64x128 image is drawn,
                with (w,h) set (10,10), it will show up as 10x20.
                if False, the image will have the exact dimensions set in (w,h).
                
                Note that this does not effect square images.
            Cull:
                if set to true, this image will not be drawn if off screen.
                (This seems to not work right sometimes).
            z: Depth. keep it between 100 and -100
        """
        if Cull:
            cw,ch = 0,0
            if UseRatio:
                cw = image.rx*w
                ch = image.ry*h;
            else:
                cw = w
                ch = h
            d = 1
            dy = 1
            if x > self.camx:
                d = -1
            if y > self.camy:
                dy = -1
            if not self.hud_mode:
                if not ((abs(self.camx-(x+(d*(cw/2)))) < ((self.ratio_x/2)*self.zoom)) and (abs(self.camy-(y+(dy*((ch/2))))) < ((self.ratio_y/2)*self.zoom))):
                    return
            else:
                if not ((abs(x+(cw/2)) < (self.ratio_x/2)) and (abs(y+(ch/2)) < (self.ratio_y/2))):
                    return

        glPushMatrix();

        glTranslatef( x, y, z );

        glRotatef(rot,0,0,1);

        glColor4f(r,g,b,a)

        if UseRatio:
            glScalef(image.rx*w,image.ry*h,1);
        else:
            glScalef(w,h,1);

        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_EQUAL, 1.0)  
        glDepthMask(GL_TRUE)        
        glCallList(image.quad)
        glAlphaFunc(GL_LESS,1.0)
        glDepthMask(GL_FALSE)   
        glCallList(image.quad)
        glDisable(GL_ALPHA_TEST)
        glDepthMask(GL_TRUE)


        glPopMatrix();

    def DrawQuad(self,x,y,w,h,a,r,g,b,rot, z = 0):
        """Draw a Quad to the screen.

        Parameters:
            
            x,y:   position.
        
            w,h:   dimensions.
        
            a:     transperency.
        
            rot:   angle/rotation.

            r,g,b: the quads color.
        
            z: Depth. keep it between 100 and -100
        """

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, self.quad_v_gl)
        glDisable(GL_TEXTURE_2D)

        glPushMatrix();

        glTranslatef( x, y, z );

        glRotatef(rot,0,0,1);

        glColor4f(r,b,g,a)
            
        glScalef(w,h,1);

        glDisable(GL_ALPHA_TEST)
        glDrawArrays(GL_QUADS, 0, 4)

        glPopMatrix();

        glDisableClientState(GL_VERTEX_ARRAY);
        glEnable(GL_TEXTURE_2D)
        
    def IsRunning(self):
        """If the window has not been closed, this will return True"""
        if pygame.event.peek(pygame.QUIT):
                return False
        pygame.event.pump()
        return True

    def PreRender(self, r, b, g):
        """Prepares the screen for drawing.

        Parameters:
                r,g,b: background color
        """
        self.ticks = pygame.time.get_ticks()
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glClearColor( r, g, b, 1 );
        
    def SetView(self, viewport, camx, camy, zoom, NoDepth = False, angle = 0):
        """
        Sets viewport.
        Parameters:
            viewport: the viewport (duh)
            camx,camy: camera position
            zoom: the zoom.
            NoDepth: if this is set to True, there will be no depth
            angle: rotates the camera. This WILL mess up MouseCoordsToWorldCoords
        """
        self.camx = camx
        self.camy = camy
        self.zoom = zoom
        self.ratio_x = viewport.resx
        self.ratio_y = viewport.resy

        ang = (angle * math.pi / 180.0)
    
        rx = math.sin(ang)
        ry = math.cos(ang)
        
        if NoDepth:
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_ALPHA_TEST)
        else:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_ALPHA_TEST)

        glViewport( int(viewport.x*self.screen_w), int( (((1.0)-viewport.y)-viewport.h) * self.screen_h), int(viewport.w*self.screen_w), int(viewport.h*self.screen_h));
        
        glMatrixMode( GL_PROJECTION );
        glLoadIdentity();
        glOrtho( (-viewport.resx/2)*zoom, (viewport.resx/2)*zoom, (viewport.resy/2)*zoom, (-viewport.resy/2)*zoom, -100, 100 );

        glMatrixMode( GL_MODELVIEW );

        glLoadIdentity();
        gluLookAt(camx,camy,20, camx,camy,0, rx,ry,0);

    def PostRender(self):
        """
        Finish rendering, update the screen, etc..
        """
        pygame.display.flip()
        self.loop = 0
        self.hud_mode = False

    def GetTicks(self):
        """
        get Milliseconds since the engine started.
        (This is pretty much pygame.time.get_ticks())
        """
        return pygame.time.get_ticks()

    def MouseCoordsToWorldCoords(self, mousex, mousey, camx, camy, zoom, viewport, cam_effect = True):
        """
        converts screen coords to world coords.
        Parameters:
            mousex,mousey: mouse coordinates (in pixels).
            camx,camy: camera position
            zoom: zoom.
            viewport: the viewport your using (or are going to use)
            cam_effect: If false, camx,camy do not effect anything.
        Returns:
            x,y: World coords.
        """
        wx, wy = 0.0,0.0

        cx = (viewport.x*self.screen_w)
        cy = (viewport.y*self.screen_h)

        wx = (( ( ( float(viewport.resx*(1/viewport.w)) * float(mousex - cx) )/self.screen_w ) - viewport.resx/2) + (camx/zoom))*zoom
        wy = (( ( ( float(viewport.resy*(1/viewport.h)) * float(mousey - cy) )/self.screen_h ) - viewport.resy/2) + (camy/zoom))*zoom

        return wx,wy
    

        
