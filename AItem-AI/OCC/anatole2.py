from OCC.Display.SimpleGui import init_display
from OCC.Extend.DataExchange import read_step_file

# Charger le fichier STEP
file_path = 'D:/anato/Documents/CNAM/DefiChalenge/AItem-AI/3D/M3D-217578_--A_CATPART_1.stp' 
shape = read_step_file(file_path)

# Initialiser la fenêtre de visualisation
display, start_display, add_menu, add_function_to_menu = init_display()

# Ajouter la forme à la fenêtre de visualisation
display.DisplayShape(shape, update=True)

# Démarrer la boucle de visualisation
start_display()