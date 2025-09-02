import pygame
import sys
import os # For saving files  

pygame.init()

SCREEN_WIDTH = 1000  # Increased width
SCREEN_HEIGHT = 800  # Increased height
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Drawing App")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
TOOLBAR_BACKGROUND = (60, 60, 60) 

drawing_color = BLACK
drawing_mode = "pen"  # "pen", "line", "rect", "circle", "eraser", "fill"
drawing = False
start_pos = None  
current_pos = None 

brush_size = 2 # Initial brush thickness
min_brush_size = 1
max_brush_size = 20

fill_mode = "outline" # "outline" or "fill" for shapes

# Toolbar height definition
BUTTON_WIDTH = 70
BUTTON_HEIGHT = 30
BUTTON_MARGIN = 8
TOOLBAR_HEIGHT = 3 * BUTTON_HEIGHT + 4 * BUTTON_MARGIN + 20 # Added extra 20px for text clarity

drawing_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
drawing_surface.fill(WHITE) 

history = []
history_index = -1
MAX_HISTORY_SIZE = 50 # Needs work

def add_to_history():
    """Saves the current state of the drawing_surface to history."""
    global history, history_index

    if history_index < len(history) - 1:
        history = history[:history_index + 1]

    history.append(drawing_surface.copy())
    history_index = len(history) - 1

    if len(history) > MAX_HISTORY_SIZE:
        history.pop(0) 
        history_index -= 1 

add_to_history()

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK, action=None, mode=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action
        self.mode = mode 

    def draw(self, surface, current_active_mode=None, current_color=None, current_fill_mode=None):
        # Highlight if this button's mode is active
        if self.mode and self.mode == current_active_mode:
            pygame.draw.rect(surface, YELLOW, self.rect.inflate(4, 4), 2) 
        
        # Highlight current color button
        if self.action == "set_color" and self.color == current_color:
             pygame.draw.rect(surface, LIGHT_GRAY, self.rect.inflate(4, 4), 2) 

        # Highlight fill mode button
        if self.action == "set_fill_outline":
            if self.mode == current_fill_mode:
                pygame.draw.rect(surface, YELLOW, self.rect.inflate(4, 4), 2) 

        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        
        if self.text:
            font = pygame.font.Font(None, 24)
            text_surf = font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Create Buttons 

# Row 1: Color buttons
color_buttons = []
colors = [BLACK, WHITE, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, CYAN]
start_x_colors = BUTTON_MARGIN
for i, color in enumerate(colors):
    btn = Button(start_x_colors + i * (BUTTON_WIDTH + BUTTON_MARGIN),
                 BUTTON_MARGIN, # Y position for first row
                 BUTTON_WIDTH, BUTTON_HEIGHT,
                 "", color, action="set_color")
    color_buttons.append(btn)

# Row 2: Tool buttons
tool_buttons = []
tool_names = ["Pen", "Line", "Rect", "Circle", "Eraser", "Fill"]
modes = ["pen", "line", "rect", "circle", "eraser", "fill"]
start_x_tools = BUTTON_MARGIN
for i, (name, mode) in enumerate(zip(tool_names, modes)):
    btn = Button(start_x_tools + i * (BUTTON_WIDTH + BUTTON_MARGIN),
                 BUTTON_MARGIN * 2 + BUTTON_HEIGHT, # Y position for second row
                 BUTTON_WIDTH, BUTTON_HEIGHT,
                 name, LIGHT_GRAY, BLACK, action="set_mode", mode=mode)
    tool_buttons.append(btn)

# Row 3: Utility buttons (Size, Fill, Undo, Redo, Save, Clear)
utility_buttons = []
# Size Down
utility_buttons.append(Button(BUTTON_MARGIN,
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Size -", LIGHT_GRAY, BLACK, action="decrease_size"))
# Size Up
utility_buttons.append(Button(BUTTON_MARGIN * 2 + BUTTON_WIDTH,
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Size +", LIGHT_GRAY, BLACK, action="increase_size"))

# Fill/Outline Toggle - now two separate buttons for clarity
utility_buttons.append(Button(BUTTON_MARGIN * 3 + BUTTON_WIDTH * 2,
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Outline", LIGHT_GRAY, BLACK, action="set_fill_outline", mode="outline"))
utility_buttons.append(Button(BUTTON_MARGIN * 4 + BUTTON_WIDTH * 3,
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Fill", LIGHT_GRAY, BLACK, action="set_fill_outline", mode="fill"))

# Undo button
utility_buttons.append(Button(BUTTON_MARGIN * 5 + BUTTON_WIDTH * 4,
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Undo", LIGHT_GRAY, BLACK, action="undo"))
# Redo button
utility_buttons.append(Button(BUTTON_MARGIN * 6 + BUTTON_WIDTH * 5,
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Redo", LIGHT_GRAY, BLACK, action="redo"))
# Save button
utility_buttons.append(Button(BUTTON_MARGIN * 7 + BUTTON_WIDTH * 6, # Adjusted X for Save
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Save", GREEN, WHITE, action="save_drawing"))
# Clear button
utility_buttons.append(Button(SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN, # Align to right
                              BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2, # Y position for third row
                              BUTTON_WIDTH, BUTTON_HEIGHT,
                              "Clear", RED, WHITE, action="clear_canvas"))


all_buttons = color_buttons + tool_buttons + utility_buttons

def save_drawing():
    """Saves the current drawing_surface to a PNG file."""
    filename = "my_drawing.png" 
    try:
        # Create a temporary surface to draw the canvas content only
        # This prevents saving the toolbar background as part of the drawing
        temp_save_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
        temp_save_surface.blit(drawing_surface, (0, 0)) 
        pygame.image.save(temp_save_surface, filename)
        print(f"Drawing saved as {filename}")
    except Exception as e:
        print(f"Error saving drawing: {e}")

def undo():
    """Reverts the drawing_surface to the previous state in history."""
    global drawing_surface, history_index
    if history_index > 0:
        history_index -= 1
        drawing_surface.blit(history[history_index], (0, 0)) # Load previous state
        print(f"Undo: Current history index {history_index}")
    else:
        print("Nothing to undo.")

def redo():
    """Reapplies the drawing_surface to the next state in history."""
    global drawing_surface, history_index
    if history_index < len(history) - 1:
        history_index += 1
        drawing_surface.blit(history[history_index], (0, 0)) # Load next state
        print(f"Redo: Current history index {history_index}")
    else:
        print("Nothing to redo.")

def flood_fill(start_point_screen, target_color, fill_color):
    """
    Performs an iterative flood fill algorithm on the drawing_surface.
    start_point_screen: (x, y) tuple (screen coordinates) where the fill starts.
    target_color: The color of the area to be filled (RGB tuple).
    fill_color: The new color to fill with (RGB tuple).
    """
    # Convert screen coordinates to drawing_surface coordinates
    start_point_canvas = (start_point_screen[0], start_point_screen[1] - TOOLBAR_HEIGHT)

    # Ensure the start point is within the canvas bounds
    if not (0 <= start_point_canvas[0] < drawing_surface.get_width() and \
            0 <= start_point_canvas[1] < drawing_surface.get_height()):
        return

    # Get pixel color at start_point_canvas to determine actual target_color
    try:
        current_target_color_at_start = drawing_surface.get_at(start_point_canvas)[:3] # Get RGB
    except IndexError: # Should not happen with bounds check, but good for robustness
        return

    # If the clicked color is already the fill color, do nothing
    if current_target_color_at_start == fill_color:
        return 

    stack = [start_point_canvas] # Use canvas coordinates for the stack
    
    # The actual target color for the fill is the color at the starting pixel
    actual_target_color = current_target_color_at_start

    canvas_width, canvas_height = drawing_surface.get_size()

    while stack:
        x, y = stack.pop()

        # Check bounds and if the pixel is the actual target color
        if 0 <= x < canvas_width and 0 <= y < canvas_height and \
           drawing_surface.get_at((x, y))[:3] == actual_target_color: # Compare RGB
            
            drawing_surface.set_at((x, y), fill_color)

            # Add neighbors to stack
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse button down event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos

                # Check if a button was clicked
                button_clicked = False
                for button in all_buttons:
                    if button.is_clicked(event.pos):
                        button_clicked = True
                        if button.action == "set_color":
                            drawing_color = button.color
                        elif button.action == "set_mode":
                            drawing_mode = button.mode
                        elif button.action == "clear_canvas":
                            drawing_surface.fill(WHITE) # Clear the drawing surface
                            add_to_history() # Save clear action to history
                        elif button.action == "increase_size":
                            brush_size = min(brush_size + 1, max_brush_size)
                        elif button.action == "decrease_size":
                            brush_size = max(brush_size - 1, min_brush_size)
                        elif button.action == "set_fill_outline":
                            fill_mode = button.mode
                        elif button.action == "save_drawing":
                            save_drawing()
                        elif button.action == "undo":
                            undo()
                        elif button.action == "redo":
                            redo()
                        break # Only one button can be clicked at a time

                # If no button was clicked and click is on canvas area
                if not button_clicked and mouse_y > TOOLBAR_HEIGHT:
                    drawing = True
                    start_pos = event.pos # Store screen-relative start position
                    current_pos = event.pos # Store screen-relative current position
                    
                    # Convert screen Y to canvas Y for drawing operations
                    canvas_y = mouse_y - TOOLBAR_HEIGHT

                    if drawing_mode == "pen":
                        pygame.draw.circle(drawing_surface, drawing_color, (mouse_x, canvas_y), brush_size // 2) # Initial dot
                    elif drawing_mode == "eraser":
                        pygame.draw.circle(drawing_surface, WHITE, (mouse_x, canvas_y), brush_size // 2) # Initial dot for eraser
                    elif drawing_mode == "fill":
                        flood_fill(event.pos, drawing_color, drawing_color) # Pass screen coordinates for start_point
                        add_to_history() # Save fill action to history
                        drawing = False # Fill is a single click action


        # Mouse motion event (dragging)
        if event.type == pygame.MOUSEMOTION:
            # Only draw if drawing is active and left mouse button is pressed
            if drawing and pygame.mouse.get_pressed()[0]:
                current_pos = event.pos # Update screen-relative current position
                
                # Ensure drawing only on canvas area
                if current_pos[1] > TOOLBAR_HEIGHT: 
                    # Convert screen coordinates to canvas coordinates for drawing
                    prev_canvas_pos = (event.pos[0] - event.rel[0], event.pos[1] - event.rel[1] - TOOLBAR_HEIGHT)
                    current_canvas_pos = (current_pos[0], current_pos[1] - TOOLBAR_HEIGHT)

                    if drawing_mode == "pen":
                        pygame.draw.line(drawing_surface, drawing_color, prev_canvas_pos, current_canvas_pos, brush_size)
                    elif drawing_mode == "eraser":
                        pygame.draw.line(drawing_surface, WHITE, prev_canvas_pos, current_canvas_pos, brush_size)

        # Mouse button up event
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if drawing and drawing_mode not in ["pen", "eraser", "fill"]: # Shapes are finalized on mouse up
                    end_pos = event.pos # Screen-relative end position
                    
                    # Clamp end_pos to canvas boundaries if released in toolbar or outside screen
                    if end_pos[1] < TOOLBAR_HEIGHT: end_pos = (end_pos[0], TOOLBAR_HEIGHT)
                    if end_pos[0] < 0: end_pos = (0, end_pos[1])
                    if end_pos[0] > SCREEN_WIDTH: end_pos = (SCREEN_WIDTH, end_pos[1])
                    if end_pos[1] > SCREEN_HEIGHT: end_pos = (end_pos[0], SCREEN_HEIGHT)

                    # Convert screen coordinates to canvas coordinates for drawing
                    start_canvas_pos = (start_pos[0], start_pos[1] - TOOLBAR_HEIGHT)
                    end_canvas_pos = (end_pos[0], end_pos[1] - TOOLBAR_HEIGHT)

                    thickness = brush_size if fill_mode == "outline" else 0 # 0 for filled shapes

                    if drawing_mode == "line":
                        pygame.draw.line(drawing_surface, drawing_color, start_canvas_pos, end_canvas_pos, brush_size)
                    elif drawing_mode == "rect":
                        rect_x = min(start_canvas_pos[0], end_canvas_pos[0])
                        rect_y = min(start_canvas_pos[1], end_canvas_pos[1])
                        rect_width = abs(start_canvas_pos[0] - end_canvas_pos[0])
                        rect_height = abs(start_canvas_pos[1] - end_canvas_pos[1])
                        pygame.draw.rect(drawing_surface, drawing_color, (rect_x, rect_y, rect_width, rect_height), thickness)
                    elif drawing_mode == "circle":
                        center_x = (start_canvas_pos[0] + end_canvas_pos[0]) // 2
                        center_y = (start_canvas_pos[1] + end_canvas_pos[1]) // 2
                        radius = int(max(abs(end_canvas_pos[0] - center_x), abs(end_canvas_pos[1] - center_y)))
                        if radius > 0: # Avoid drawing zero-radius circles
                            pygame.draw.circle(drawing_surface, drawing_color, (center_x, center_y), radius, thickness)
                    
                    add_to_history() # Save shape action to history
                    
                # Reset drawing state for all modes after mouse up
                drawing = False
                start_pos = None
                current_pos = None

    screen.fill(DARK_GRAY) # Background for the entire window

    # Draw the toolbar background
    pygame.draw.rect(screen, TOOLBAR_BACKGROUND, (0, 0, SCREEN_WIDTH, TOOLBAR_HEIGHT))

    # Blit the drawing surface onto the main screen (below the toolbar)
    screen.blit(drawing_surface, (0, TOOLBAR_HEIGHT))

    # Draw live preview for line, rect, circle modes
    if drawing and start_pos and current_pos and drawing_mode not in ["pen", "eraser", "fill"]:
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # Transparent surface for preview
        temp_surface.fill((0,0,0,0)) # Ensure it's fully transparent
        
        preview_color = drawing_color + (100,) # Add alpha for semi-transparency
        thickness = brush_size if fill_mode == "outline" else 0

        # Convert screen-relative positions to canvas-relative for preview drawing
        start_canvas_pos_preview = (start_pos[0], start_pos[1] - TOOLBAR_HEIGHT)
        current_canvas_pos_preview = (current_pos[0], current_pos[1] - TOOLBAR_HEIGHT)

        if drawing_mode == "line":
            pygame.draw.line(temp_surface, preview_color, start_canvas_pos_preview, current_canvas_pos_preview, brush_size)
        elif drawing_mode == "rect":
            rect_x = min(start_canvas_pos_preview[0], current_canvas_pos_preview[0])
            rect_y = min(start_canvas_pos_preview[1], current_canvas_pos_preview[1])
            rect_width = abs(start_canvas_pos_preview[0] - current_canvas_pos_preview[0])
            rect_height = abs(start_canvas_pos_preview[1] - current_canvas_pos_preview[1])
            pygame.draw.rect(temp_surface, preview_color, (rect_x, rect_y, rect_width, rect_height), thickness)
        elif drawing_mode == "circle":
            center_x = (start_canvas_pos_preview[0] + current_canvas_pos_preview[0]) // 2
            center_y = (start_canvas_pos_preview[1] + current_canvas_pos_preview[1]) // 2
            radius = int(max(abs(current_canvas_pos_preview[0] - center_x), abs(current_canvas_pos_preview[1] - center_y)))
            if radius > 0:
                pygame.draw.circle(temp_surface, preview_color, (center_x, center_y), radius, thickness)
        
        screen.blit(temp_surface, (0, TOOLBAR_HEIGHT))

    # Draw UI elements on top of everything
    for button in all_buttons:
        button.draw(screen, drawing_mode, drawing_color, fill_mode) # Pass current drawing mode, color, and fill mode

    # Draw current brush size display
    font = pygame.font.Font(None, 24)
    size_text = font.render(f"Size: {brush_size}", True, WHITE)
    # Positioned relative to the right side of the toolbar
    screen.blit(size_text, (SCREEN_WIDTH - size_text.get_width() - BUTTON_MARGIN, BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2 + 5))

    # Draw current fill mode display (for shapes)
    fill_mode_text = font.render(f"Fill: {fill_mode.capitalize()}", True, WHITE)
    # Positioned below size text
    screen.blit(fill_mode_text, (SCREEN_WIDTH - fill_mode_text.get_width() - BUTTON_MARGIN, BUTTON_MARGIN * 3 + BUTTON_HEIGHT * 2 + 5 + size_text.get_height() + 5))


    # Draw live brush size preview on the canvas (when pen/eraser is active)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_y > TOOLBAR_HEIGHT and (drawing_mode == "pen" or drawing_mode == "eraser"):
        preview_color = drawing_color if drawing_mode == "pen" else WHITE
        # Draw a semi-transparent circle for the preview
        pygame.draw.circle(screen, preview_color + (150,), (mouse_x, mouse_y), brush_size // 2, 0)


    pygame.display.flip() # Update the full display surface

pygame.quit()
sys.exit()

