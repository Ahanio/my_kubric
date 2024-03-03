# Copyright 2022 The Kubric Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import kubric as kb
from kubric.renderer.blender import Blender as KubricRenderer

import numpy as np
import bpy
from tqdm import tqdm

logging.basicConfig(level="INFO")

num_cams = 50
output_dir = "results/cube_renders"
hdri_path = 'assets/hdris/courtyard.exr'
debug=False

num_train_frames = 100
num_validation_frames = 100
num_test_frames = 200 #200

# --- create scene and attach a renderer to it
scene = kb.Scene(resolution=(512, 512))
# renderer = KubricRenderer(scene)
renderer = KubricRenderer(
    scene,
    './',
    use_denoising=True,
    adaptive_sampling=True,
    custom_scene="custom_scene.blend",
    samples_per_pixel=256)

bpy_scene = bpy.context.scene

# --- populate the scene with objects, lights, cameras
# seed = seed if seed else np.random.randint(0, 2147483647)
# print('SEED:', seed)
# rng = np.random.RandomState(seed=seed)

# instance = kb.Cube(name="cube", scale=0.9, position=(0, 0, 0))
# instance.material = kb.PrincipledBSDFMaterial(name="material")
# instance.material.metallic = 0.0
# instance.material.roughness = 1.0
# scene += instance

# --- Setting up light
# scene += kb.DirectionalLight(name="sun", position=(-1, -0.5, 3),
#                              look_at=(0, 0, 0), intensity=1.5)
scene.ambient_illumination = kb.Color(1, 1, 1)
# renderer._set_ambient_light_hdri(hdri_path)


# --- Setting camera
camera = kb.PerspectiveCamera()
scene += camera

def update_camera():
#   position = rng.normal(size=(3, ))
#   position *= 4 / np.linalg.norm(position)
#   position[2] = np.abs(position[2])
#   camera.position = position
    camera.position = kb.sample_point_in_half_sphere_shell(3.8, 5, -100)
    camera.look_at((0, 0, 0))
    return camera.matrix_world

def output_split(split_name, n_frames):
  frames = []

  # --- Render a set of frames from random camera poses
  for i in tqdm(range(n_frames)):
    matrix = update_camera()

    frame = renderer.render_still()

    # frame["segmentation"] = kb.adjust_segmentation_idxs(frame["segmentation"], scene.assets, [])
    
    kb.write_png(filename=f"{output_dir}/{split_name}/{i}.png", data=frame["rgba"][...,:-1])
    # kb.write_palette_png(filename=f"{output_dir}/{split_name}/{i}_segmentation.png", data=frame["segmentation"])

    frame_data = {
      "transform_matrix": matrix.tolist(),
      "file_path": f"{split_name}/{i}",
    }
    frames.append(frame_data)

    # --- Write the JSON descriptor for this split
    kb.write_json(filename=f"{output_dir}/transforms_{split_name}.json", data={
    "camera_angle_x": camera.field_of_view,
    "frames": frames,
    })

# renderer.save_state(f"{output_dir}/cube_random_text.blend")
output_split("train", num_train_frames)
output_split("val", num_validation_frames)
output_split("test", num_test_frames)

kb.done()


# scene.frame_end = num_cams
# scene.camera = kb.PerspectiveCamera()
# for frame in range(1, num_cams+1):
#   scene.camera.position = kb.sample_point_in_half_sphere_shell(3.5, 4.5, -100)
#   scene.camera.look_at((0, 0, 0))
#   scene.camera.keyframe_insert("position", frame)
#   scene.camera.keyframe_insert("quaternion", frame)

# # --- render (and save the blender file)
# renderer.save_state("output/sphere_random_text.blend")
# data_stack = renderer.render()

# # --- save the output as pngs
# kb.file_io.write_rgba_batch(data_stack["rgba"], output_dir)

# # --- Collect metadata
# logging.info("Collecting and storing metadata for each object.")
# data = {
#     "camera": kb.get_camera_info(scene.camera),
# }

# kb.file_io.write_json(filename=f"{output_dir}/metadata.json", data=data)
# kb.done()