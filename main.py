import kociemba
from cubeDetecter import find_squares

def general_instructions():
    print("\n" + "="*50)
    print("      RUBIK'S CUBE SOLVER - COMPUTER VISION")
    print("="*50)
    print("RULES FOR A PERFECT CAPTURE:")
    print("1. ALIGNMENT: Keep the face parallel to the camera.")
    print("2. LIGHT: Avoid direct flash or heavy shadows.")
    print("3. STABILITY: Hold the cube steady during the photo.")
    print("4. BACKGROUND: Use a neutral surface.")
    print("="*50 + "\n")

def instructions(face):
    print("Hi, so here are the instructions to use the program:")
    order = {
        'U': "Look at the Top face. Keep the 'Front' side facing the screen.",
        'R': "Keep Top pointing UP. Rotate cube 90° LEFT to see the Right face.",
        'F': "Keep Top pointing UP. Rotate cube back to the Front face.",
        'D': "From Front, tilt the cube UP to see the Bottom face.",
        'L': "Keep Top pointing UP. Rotate cube 90° RIGHT to see the Left face.",
        'B': "Keep Top pointing UP. Rotate cube 90° Again to see the Back face."
    }
    print(f"-----\nPhoto of Face {face}-------")
    print(f"Step: {order[face]}")
    print("Cube alinhed with the camera, without reflections and neutral background.")

def convert_to_kociemba_format(cube):
    # Here we transform the colors into the notation expected by kociemba
    # Always the program see the central color, the program will know the face
    faces_order = ['U', 'R', 'F', 'D', 'L', 'B']
    kociemba_string = ""
    color_to_face = {}

    for face in faces_order:
        center_color = cube[face][4]
        color_to_face[center_color] = face

    for face in faces_order:
        for color in cube[face]:
            kociemba_string += color_to_face[color]

    return kociemba_string

def translate_solution(solution):
    if not solution:
        return "The cube is already solved"
    
    translation_map = {
        'U': "Up", 'D': 'Down', 'R': 'Right',
        'L': 'Left', 'F': 'Front', 'B': 'Back' 
    }

    steps = solution.split()
    explained_steps = []

    for step in steps:
        face = step[0]
        direction = step[1:] if len(step) > 1 else ''

        name = translation_map[face]
        if direction == '':
            moviment = "Turn clockwise"
        elif direction == "'":
            moviment = "Turn counterclockwise"
        else:
            moviment = "Turn 180 degrees"
        
        explained_steps.append(f"{name}: {moviment}")

    return explained_steps
        
def solve_cube():
    general_instructions()
    faces_order = ['U', 'R', 'F', 'D', 'L', 'B']
    cube = {}

    for face in faces_order:
        while True:
            instructions(face)
            path = input(f"Enter the image path for face {face}: .jpeg or .jpg:\n")
            colors_detected = find_squares(path)
            if colors_detected:
                confirm = input(f"Colors detected for face {face}: {colors_detected}. Is this correct? (y/n): ").lower()
                if confirm == 'y':
                    cube[face] = colors_detected
                    break
                else:
                    print("Try again, with a diferent angle or check the examples in the Readme in GitHub.")
            else:
                print(f"Error processing face {face}. Please check the image or take another.")            

    try:
        cube_string = convert_to_kociemba_format(cube)
        print(f"\nGenerated String: {cube_string}")

        cube_solved = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        counts = {letra: cube_string.count(letra) for letra in faces_order}
        print(f"Color distribution: {counts}")

        if cube_string == cube_solved:
            print("The cube is already solved!")
            return
        if any(count != 9 for count in counts.values()):
            print("ERROR: Invalid distribution. Every face must have exactly 9 stickers.")
            return
        
        solution = kociemba.solve(cube_string)
        print("\n\nSolution:\n", solution)
        moviments_explained = translate_solution(solution)
        for i, passo in enumerate(moviments_explained, 1):
            print(f"{i}. {passo}")
    except Exception as e:
        print("Error solving the cube:", e)
        print("Check if the order of the photos is correct and id the photos aren't with bad light(too bright or dark) or background.")

if __name__ == "__main__":
    solve_cube()