"""
Plot un modèle 3D .obj avec plotly
"""
import os
import sys
import torch
from pytorch3d.structures import Meshes
from pytorch3d.vis.plotly_vis import AxisArgs, plot_batch_individually, plot_scene
from pytorch3d.io import load_objs_as_meshes, load_obj
from plot_image_grid import image_grid


device = torch.device("cpu")
obj_filename = 'D:/anato/Documents/CNAM/DefiChalenge/fichiers3D - Copie/[Challenge CNAM] 3D - Package1/3D/M3D-180570_--A_CATPART_1.obj'
verts, faces, _ = load_obj(obj_filename, device = device)

# print(verts)
# print(faces)

verts, faces_idx, _ = load_obj(obj_filename)
faces = faces_idx.verts_idx

# Initialize each vertex to be white in color.
verts_rgb = torch.ones_like(verts)[None]/2  # (1, V, 3)


# Create a Meshes object
mesh = Meshes(
    verts=[verts.to(device)],   
    faces=[faces.to(device)],
)

# Render the plotly figure
fig = plot_scene({
    "subplot1": {
        "cow_mesh": mesh
    }
})
fig.show()