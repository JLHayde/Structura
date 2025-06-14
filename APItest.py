import os
import shutil

from log_config import get_logger
import structura_core


logger = get_logger(file_log=False, level="debug")


structura_core.debug = True
files_to_convert = {
    "gems": {
        "file": "test_structures/All Blocks World/gems and redstone.mcstructure",
        "offset": [-32, 0, -32],
    },
    "stone": {
        "file": "test_structures/All Blocks World/Stones.mcstructure",
        "offset": [-30, 0, -32],
    },
    "wood": {
        "file": "test_structures/All Blocks World/wood.mcstructure",
        "offset": [-31, 0, -31],
    },
    "decor": {
        "file": "test_structures/All Blocks World/decorative.mcstructure",
        "offset": [-32, 0, -31],
    },
    "wood2": {
        "file": "test_structures/All Blocks World/wood2.mcstructure",
        "offset": [-32, 0, -31],
    },
}
try:
    shutil.rmtree("tmp/")
except Exception:
    pass
if os.path.exists("tmp/all_blocks.mcpack"):
    os.remove("tmp/all_blocks.mcpack")
if os.path.exists("tmp/all_blocks Nametags.txt"):
    os.remove("tmp/all_blocks Nametags.txt")
structura_base = structura_core.Structura("tmp/all_blocks")
structura_base.set_opacity(20)

for name_tag, info in files_to_convert.items():
    logger.info(f"Adding '{name_tag}', {info}")
    structura_base.add_model(name_tag, info["file"])
    structura_base.set_model_offset(name_tag, info["offset"])

structura_base.generate_nametag_file()
structura_base.generate_with_nametags()

logger.info("Pack compiled to {}".format(structura_base.compile_pack()))
logger.info("Block lists created:")
for i in structura_base.make_nametag_block_lists():
    logger.info(i)
logger.info("API Test complete.")
