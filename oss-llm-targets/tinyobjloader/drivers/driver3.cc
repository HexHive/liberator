#include <fuzzer/FuzzedDataProvider.h>

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "tiny_obj_loader.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  FuzzedDataProvider provider(data, size);
  const std::string material_name = provider.ConsumeRandomLengthString();
  const std::string material_ambient_texture = provider.ConsumeRandomLengthString();
  const std::string material_diffuse_texture = provider.ConsumeRandomLengthString();
  const std::string material_specular_texture = provider.ConsumeRandomLengthString();
  const std::string material_specular_highlight_texture = provider.ConsumeRandomLengthString();
  const std::string material_bump_texture = provider.ConsumeRandomLengthString();
  const std::string material_displacement_texture = provider.ConsumeRandomLengthString();
  const std::string material_alpha_texture = provider.ConsumeRandomLengthString();
  const std::string material_reflection_texture = provider.ConsumeRandomLengthString();
  tinyobj::material_t material;
  material.name = material_name;
  material.ambient_texname = material_ambient_texture;
  material.diffuse_texname = material_diffuse_texture;
  material.specular_texname = material_specular_texture;
  material.specular_highlight_texname = material_specular_highlight_texture;
  material.bump_texname = material_bump_texture;
  material.displacement_texname = material_displacement_texture;
  material.alpha_texname = material_alpha_texture;
  material.reflection_texname = material_reflection_texture;
  tinyobj::material_t new_material(material);
  return 0;
}


