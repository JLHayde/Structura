import traceback

import nbtlib.nbt

import armor_stand_geo_class as asgc
import armor_stand_class ,structure_reader ,animation_class ,manifest ,os ,glob ,json ,shutil 
import render_controller_class as rcc
import big_render_controller as brc
from shutil import copyfile
from zipfile import ZIP_DEFLATED, ZipFile
import time
import os
from log_config import get_logger

debug=False
logger = get_logger(__name__)

class UnsupportedBlock:
    """
    Holds all the properties of an unsupported block.
    Can be compared to filter.
    """
    def __init__(self, pos: tuple[int, int, int], block: nbtlib.nbt.Compound, variant: str):
        self.pos = pos
        self.block = block
        self.variant = variant

    def __str__(self):
        return "x:{} Y:{} Z:{}, Block:{}, Variant: {}".format(
        self.pos[0], self.pos[1],self.pos[2],
            self.block["name"],
            self.variant
        )
    def __eq__(self, other):
        if not isinstance(other, UnsupportedBlock):
            return NotImplemented
        return self.block["name"] == other.block["name"] and self.variant == other.variant

    def __hash__(self):
        return hash((frozenset(self.block["name"]), self.variant))

with open("lookups/nbt_defs.json") as f:
    nbt_def = json.load(f)
class structura:
    def __init__(self,pack_name):
        os.makedirs(pack_name)
        self.timers={"start":time.time(),"previous":time.time()}
        self.pack_name=pack_name
        self.structure_files={}
        self.rc=rcc.render_controller()
        self.armorstand_entity = armor_stand_class.armorstand()
        visual_name=pack_name
        self.animation = animation_class.animations()
        self.exclude_list=["minecraft:structure_block","minecraft:air"]
        self.opacity=0.8
        self.longestY=0
        self.unsupported_blocks=[]
        self.all_blocks={}
        self.icon="lookups/pack_icon.png"
        self.dead_blocks={}
    def set_icon(self,icon):
        self.icon=icon
    def set_opacity(self,opacity):
        self.opacity=opacity
    def add_model(self,name,file_name):
        self.structure_files[name]={}
        self.structure_files[name]["file"]=file_name
        self.structure_files[name]["offsets"]=None
    def set_model_offset(self,name,offset):
        self.structure_files[name]["offsets"]=offset
    def generate_nametag_file(self):
        ## temp folder would be a good idea
        name_tags=self.structure_files.keys()
        fileName="{} Nametags.txt".format(self.pack_name)
        with open(fileName,"w+") as text_file:
            text_file.write("These are the nametags used in this file\n")
            for name in name_tags:
                text_file.write("{}\n".format(name))
    def make_big_model(self,offset):
        self.rc=brc.render_controller()
        file_names=[]
        for name in list(self.structure_files.keys()):
            file_names.append(self.structure_files[name]["file"])
        struct2make=structure_reader.combined_structures(file_names,exclude_list=self.exclude_list)
        self.structure_files[""]={}
        self.structure_files[""]["offsets"]=[0,0,0]
        self.structure_files[""]["offsets"][1]= 0
        layers=12
        if (struct2make.get_size()[1]<=12):
            layers=struct2make.get_size()[1]
        for i in range(layers):
            self.armorstand_entity.add_model(str(i))
            self.rc.add_geometry(str(i))
        self.big_offset=offset
        self.all_blocks=self._add_blocks_to_geo(struct2make,"",export_big=True)
        self.armorstand_entity.export(self.pack_name)
    def generate_with_nametags(self):
        update_animation=True
        for model_name in self.structure_files.keys():
            if self.structure_files[model_name]["offsets"] is None:
                offset=[0,0,0]
            else:
                offset=self.structure_files[model_name]["offsets"]
            self.rc.add_model(model_name)
            self.armorstand_entity.add_model(model_name)
            ## temp folder would be a good idea
            copyfile(self.structure_files[model_name]["file"], "{}/{}.mcstructure".format(self.pack_name,model_name))
            if debug:
                print(self.structure_files[model_name]['offsets'])
            struct2make = structure_reader.process_structure(self.structure_files[model_name]["file"])
            blocks=self._add_blocks_to_geo(struct2make,model_name)
            self.structure_files[model_name]["block_list"]=blocks
            ##consider temp folder
            self.armorstand_entity.export(self.pack_name)## this may be in the wrong spot, but transfered from 1.5

    def get_model_block_count(self, model_name: str) -> int:
        """
        Return the total number of blocks in the model.
        :param model_name:
        :return:
        """
        model =  self.structure_files.get(model_name)
        if model is None:
            return 0

        count = 0
        for k,v in model["block_list"].items():
            count += v
        return count


    def make_nametag_block_lists(self):
        ## consider temp file
        logger.info("Generating Block list")
        file_names=[]
        for model_name in self.structure_files.keys():
            file_name="{}-{} block list.txt".format(self.pack_name,model_name)
            file_names.append(file_name)
            all_blocks = self.structure_files[model_name]["block_list"]
            with open(file_name,"w+") as text_file:
                text_file.write("This is a list of blocks, there is a known issue with variants, all blocks are reported as minecraft stores them\n")
                # Decorate Colum names
                column = f"{'Block':<25} {'Count':>4}  | {'Stacks':>5}   {'Remainder':>5} \n"
                text_file.write("_"*len(column) + "\n")
                text_file.write(column)
                text_file.write("_" * len(column) + "\n")

                for name in all_blocks.keys():
                    commonName = name.replace("minecraft:","")
                    count = all_blocks[name]
                    stacks, blocks = self._make_block_count_text(count)
                    text_file.write(f"{commonName:<25} {count:>4}  | {stacks:>5}  {blocks:>5}\n")

                text_file.write("_" * len(column) + "\n")
                block_count = self.get_model_block_count(model_name)
                text_file.write(f"Block Count: {block_count}")

        return file_names
    def make_big_blocklist(self):
        ## consider temp file
        file_name="{} block list.txt".format(self.pack_name)
        with open(file_name,"w+") as text_file:
            text_file.write("This is a list of blocks, there is a known issue with variants, all blocks are reported as minecraft stores them\n")
            for name in self.all_blocks.keys():
                commonName = name.replace("minecraft:","")
                
                text_file.write("{}: {}\n".format(commonName,self.all_blocks[name]))

    def _add_blocks_to_geo(self,struct2make,model_name,export_big=False):
        [xlen, ylen, zlen] = struct2make.get_size()
        if export_big:
            self.structure_files[model_name]['offsets'][0]-=xlen.item()+7
            self.structure_files[model_name]['offsets'][2]-=zlen.item()+7
        armorstand = asgc.armorstandgeo(model_name,alpha = self.opacity, size=[xlen, ylen, zlen], offsets=self.structure_files[model_name]['offsets'])

        if ylen > self.longestY:
            update_animation=True
            longestY = ylen
        else:
            update_animation=False
        for y in range(ylen):
            
            #creates the layer for controlling. Note there is implied formating here
            #for layer names
            if y<12:
                armorstand.make_layer(y)
                #adds links the layer name to an animation
                if update_animation and not export_big:
                    self.animation.insert_layer(y)
            non_air=struct2make.get_layer_blocks(y)
            for loc in non_air:
                x=int(loc[0])
                z=int(loc[1])
                block = struct2make.get_block(x, y, z)
                blk_name=block["name"].replace("minecraft:", "")
                blockProp=self._process_block(block)
                rot = blockProp[0]
                top = blockProp[1]
                variant = blockProp[2]
                open_bit = blockProp[3]
                data = blockProp[4]
                if debug:
                    armorstand.make_block(x, y, z, blk_name, rot = rot, top = top,variant = variant, trap_open=open_bit, data=data, big = export_big)
                else:
                    try:
                        armorstand.make_block(x, y, z, blk_name, rot = rot, top = top,variant = variant, trap_open=open_bit, data=data, big = export_big)
                    except Exception as e:
                        logger.warning("Unsupported block '{}' in this world and it was skipped".format(blk_name))
                        logger.debug(traceback.format_exc())
                        unsupported = UnsupportedBlock((x,y,z), block, variant)
                        self.unsupported_blocks.append(unsupported)
                        if block["name"] not in self.dead_blocks.keys():
                            self.dead_blocks[block["name"]]={}
                        if type(variant) is list:
                            variant="_".join(variant)
                        if variant not in self.dead_blocks[block["name"]].keys():
                            self.dead_blocks[block["name"]][variant]=0
                        self.dead_blocks[block["name"]][variant]+=1
            ## consider temp file
        if export_big:
            armorstand.export_big(self.pack_name)
            self.animation.export_big(self.pack_name,self.big_offset)
        else:
            armorstand.export(self.pack_name)
            self.animation.export(self.pack_name)
        return struct2make.get_block_list()
    def compile_pack(self, overwrite=False):
        ## consider temp file
        logger.info("Starting compile for pack '{}".format(self.pack_name))
        nametags=list(self.structure_files.keys())
        if len(nametags)>1:
            manifest.export(self.pack_name,nameTags=nametags)
        else:
            manifest.export(self.pack_name)
        copyfile(self.icon, f"{self.pack_name}/pack_icon.png")
        larger_render = "lookups/armor_stand.larger_render.geo.json"
        larger_render_path = f"{self.pack_name}/models/entity/armor_stand.larger_render.geo.json"
        copyfile(larger_render, larger_render_path)
        self.rc.export(self.pack_name)
        file_paths = []
        logger.info("Making Archive...")
        shutil.make_archive("{}".format(self.pack_name), 'zip', self.pack_name)
        if overwrite:
            os.remove(f'{self.pack_name}.mcpack')
        os.rename(f'{self.pack_name}.zip',f'{self.pack_name}.mcpack')
        shutil.rmtree(self.pack_name)
        self.timers["finished"]=time.time()-self.timers["previous"]
        self.timers["total"]=time.time()-self.timers["start"]

        logger.info(f"Pack Making Completed in {self.timers["total"]:.2} seconds")
        
        return f'{self.pack_name}.mcpack'

    @staticmethod
    def _make_block_count_text(count: int) -> tuple[int, int]:
        """
        Takes a block count and returns it as "Stacks, Remainder"
        Helps make block counts more readable.
        :param int count:
        :return:
        """

        whole = count // 64
        remainder = count % 64
        return whole, remainder

    def _process_block(self,block):
        rot = None
        top = False
        open_bit = False
        data=0
        variant="default"
        for key in nbt_def.keys():
            if nbt_def[key]== "variant" and key in block["states"].keys():
                variant = [key,block["states"][key]]
            if nbt_def[key] == "rot" and key in block["states"].keys():
                try:
                    rot = int(block["states"][key])
                except:
                    rot = str(block["states"][key])
                
            if nbt_def[key]== "top" and key in block["states"].keys():
                top = bool(block["states"][key])
            if nbt_def[key]== "open_bit" and "open_bit" in block["states"].keys():
                open_bit = bool(block["states"][key])
            if nbt_def[key]== "data" and key in block["states"].keys():
                data = int(block["states"][key])
            if key == "rail_direction" and key in block["states"].keys():
                data = str(block["states"][key].as_unsigned)
                if "rail_data_bit" in block["states"].keys():
                    data += "-"+str(block["states"]["rail_data_bit"].as_unsigned)

        if "wood_type" in block["states"].keys():
            variant = ["wood_type",block["states"]["wood_type"]]
            if block["name"] == "minecraft:wood":
                keys = block["states"]["wood_type"]
                if bool(block["states"]["stripped_bit"]):
                    keys+="_stripped"
                variant = ["wood",keys]
        return [rot, top, variant, open_bit, data]
    def get_skipped(self):
        ## temp folder would be a good idea
        if len(self.unsupported_blocks)>1:
            fileName="{} skipped.txt".format(self.pack_name)
            with open(fileName,"w+") as text_file:
                text_file.write("These are the skipped blocks\n")
                for skipped in self.unsupported_blocks:
                    text_file.write(f"{skipped}\n")
        return self.dead_blocks

    def get_unique_blocks_count(self):
        count = 0
        if self.structure_files:
            for k, v in self.structure_files.items():
                count += len(list(v["block_list"].keys()))

        return count


