import json
import os
import time

from utils import generate_id, generate_16_digit_timestamp, get_drive_from_path, read_json, process_image,process_audios_in_folder,template_path,process_audio,process_images_in_folder
from xstugo import tracks, segment_video,segment_audio,vocal,videos_items,sound_items,speeds_items,canvases_items,beats_items,audios,draft_materials_items,material_animations_items,text_items,text_segment_items

 
class main:
    def init_data(self):
        """
        初始化数据
        """
        self.base_path = "D:/jianying-caogao/JianyingPro Drafts" # 程序所在目录
        self.folder_path = "D:/jianying-caogao/JianyingPro Drafts/草稿"  # 草稿文件夹路径
        self.novel_name = "草稿"  # 草稿名字
        self.template_meta_info_path, self.template_meta_content_path = template_path()  # 返回两个模版的完整路径
        self.draft_content_template = read_json(self.template_meta_content_path)  # 模版1
        self.draft_meta_template = read_json(self.template_meta_info_path)  # 模版2

        self.draft_content_template['id'] = generate_id()  # 给模版ID设置唯一id
        tracks_text_data = tracks()  # 创建tracks用于存放文字信息
        tracks_text_data['type'] = 'text'  # 类型
        self.draft_content_template['tracks'].append(tracks_text_data)
        tracks_video_data = tracks()  # 创建tracks用于存放图片信息
        tracks_video_data['type'] = 'video'  # 类型
        self.draft_content_template['tracks'].append(tracks_video_data)  # 添加到模板里
        tracks_audio_data = tracks()  # 创建tracks用于存放音频信息
        tracks_audio_data['type'] = 'audio'  # 类型
        self.draft_content_template['tracks'].append(tracks_audio_data)  # 添加到模板里

        self.draft_meta_template['draft_id'] = generate_id()  # 给模版ID设置唯一id
        self.draft_meta_template[
            'draft_root_path'] = self.base_path  # 剪映的草稿路劲 如：D:\\\\software\\\\剪映\\\\JianyingPro Drafts
        self.draft_meta_template['tm_draft_create'] = int(time.time() * 1000)  # draft_meta_info.json创建时间，时间戳
        self.draft_meta_template['tm_draft_modified'] = generate_16_digit_timestamp()  # 13或16位毫秒级时间戳
        self.draft_meta_template['draft_removable_storage_device'] = get_drive_from_path(self.base_path)  # 磁盘的驱动器 如"D:"
        self.draft_meta_template['draft_fold_path'] = self.folder_path.replace('\\','/')  # 剪映安装路劲加上草稿名字 如： D:/software/剪映/JianyingPro Drafts/草稿
        self.draft_meta_template['draft_name'] = self.novel_name  # 草稿名字 如："D:/software/剪映/JianyingPro Drafts/草稿"
    def image_audio(self):
        """
        处理图片和音频 
        """
         
        # # 处理图片
        self.imagepath = "C://Users//56381//Desktop//image"
        # 这个是从存放图片的路径中读取图片，并生成图片配置，是一个字典
        image_sold = process_images_in_folder(self.imagepath)
        # 这个是拿到图片模板，通过遍历image_sold,将信息写入图片模板
        # 写入图片配置
        for index,image in enumerate(image_sold):
            videos_items_data=videos_items()
            videos_items_data['path']=image['file_path'].replace('\\','/')
            videos_items_data['material_name']=image['file_name']
            videos_items_data['width']=image['width']
            videos_items_data['height']=image['height']
            videos_items_data['id']=generate_id()
            self.draft_content_template['materials']['videos'].append(videos_items_data)  # 添加到模板里

        # ==============================canvases跟随图片数量=========
            canvases_items_data=canvases_items()
            canvases_items_data['id']=generate_id()
            self.draft_content_template['materials']['canvases'].append(canvases_items_data)  
            #=========================sound_channel_mappings=============

            sound_items_data=sound_items()
            sound_items_data['id']=generate_id()
            self.draft_content_template['materials']['sound_channel_mappings'].append(sound_items_data)  # 添加到模板里
            # ====================speeds==============================
            speeds_items_data=speeds_items()
            speeds_items_data['id']=generate_id()
            self.draft_content_template['materials']['speeds'].append(speeds_items_data)  # 添加到模板里
            # ===================material_animations======================
            material_animations_items_data=material_animations_items()
            material_animations_items_data['id']=generate_id()
            self.draft_content_template['materials']['material_animations'].append(material_animations_items_data)  # 添加到模板里
            # =================vocal_separations================
            choice_items_data=vocal()
            choice_items_data['id']=generate_id()
            self.draft_content_template['materials']['vocal_separations'].append(choice_items_data)  # 添加到模板里
              # ============================tracks-segments-video====================================
            segments_video_data = segment_video()
            segments_video_data['material_id'] = videos_items_data['id']
            segments_video_data['extra_material_refs']= [speeds_items_data['id'],canvases_items_data['id'],material_animations_items_data['id'],sound_items_data['id'],choice_items_data['id']]
            
            segments_video_data['id'] = generate_id()
            self.draft_content_template['tracks'][1]['segments'].append(segments_video_data)  # 添加到模板里
            
        
# ===========================音频处理=====================================
    def audio(self):
        
        # # 处理音频
        self.audiopath = "C://Users//56381//Desktop//audio"
        audio_sold = process_audios_in_folder(self.audiopath)
        # # 写入音频配置
        total_duration=0
        for index,audio in enumerate(audio_sold):
            
            audio_items_data=audios()
            audio_items_data['path']=audio['file_path'].replace('\\','/')
            audio_items_data['name']=audio['file_name']
            audio_items_data['duration']=audio['duration']
            total_duration += audio['duration']
            audio_items_data['id']=generate_id()
            self.draft_content_template['materials']['audios'].append(audio_items_data)  # 添加到模板里
            # ====================speeds==============================
            speeds_items_data=speeds_items()
            speeds_items_data['id']=generate_id()
            self.draft_content_template['materials']['speeds'].append(speeds_items_data)  # 添加到模板里
              # ==============================beats=============
            beats_items_data=beats_items()
            beats_items_data['id']=generate_id()
            self.draft_content_template['materials']['beats'].append(beats_items_data)  # 添加到模板里
             #=========================audio_channel_mappings=============

            sound_items_data=sound_items()
            sound_items_data['id']=generate_id()
            self.draft_content_template['materials']['sound_channel_mappings'].append(sound_items_data)  # 添加到模板里
            # =================vocal_separations================
            choice_items_data=vocal()
            choice_items_data['id']=generate_id()
            self.draft_content_template['materials']['vocal_separations'].append(choice_items_data)  # 添加到模板里
        # =============tracks-segments-audio=======
            segments_audio_data = segment_audio()
            segments_audio_data['material_id'] = audio_items_data['id']
            self.draft_content_template['tracks'][2]['segments'].append(segments_audio_data)  # 添加到模板里
            segments_audio_data['extra_material_refs'] = [speeds_items_data['id'], beats_items_data['id'],sound_items_data['id'],choice_items_data['id']]
        #=============duration===============================
            segments_audio_data['target_timerange']['duration'] = audio_items_data['duration']+1
            segments_audio_data['source_timerange']['start'] = 0
            segments_audio_data['target_timerange']['start'] = total_duration-audio_items_data['duration']
            segments_audio_data['source_timerange']['duration'] = audio_items_data['duration']
            self.draft_content_template['tracks'][1]['segments'][index]['source_timerange']['duration']=audio_items_data['duration']
            self.draft_content_template['tracks'][1]['segments'][index]['target_timerange']['duration']=audio_items_data['duration']+1
            self.draft_content_template['tracks'][1]['segments'][index]['source_timerange']['start']=0
            self.draft_content_template['tracks'][1]['segments'][index]['target_timerange']['start']=total_duration-audio_items_data['duration']
            self.draft_content_template['tracks'][0]['segments'][index]['target_timerange']['start']=total_duration-audio_items_data['duration']
            self.draft_content_template['tracks'][0]['segments'][index]['target_timerange']['duration']=audio_items_data['duration']+1
        self.draft_content_template['duration']=total_duration
   
    def text(self):
        
        
        # ==============处理文本=========
        text_path = "C:\\Users\\56381\\Desktop\\旬刊万古2.txt"
        text_path = text_path.replace('\\','/')
        with open(text_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]
            print(lines)
            for index,line in enumerate(lines):
                  # ===================material_animations======================
                material_animations_items_data=material_animations_items()
                material_animations_items_data['id']=generate_id()
                self.draft_content_template['materials']['material_animations'].append(material_animations_items_data)  # 添加到模板里
                # ====================tracks-segments-text=
                segment_text_data = text_segment_items()
                
                segment_text_data['extra_material_refs'] = [material_animations_items_data['id']]
                self.draft_content_template['tracks'][0]['segments'].append(segment_text_data)  # 添加到模板里
                text_length = len(line)
                start_index = 0
                end_index = text_length
                text_data = text_items()
               
                text_data['id'] = segment_text_data['material_id']
                text_data_content = json.loads(text_data['content'])
                
                text_data_content['text'] = line
                text_data_content['styles'][0]['range']= [start_index, end_index]
                text_data['content']= json.dumps(text_data_content, ensure_ascii=False)
               
                self.draft_content_template['materials']['texts'].append(text_data)  # 添加到模板里
    
      
    def write_data(self):
        """
        创建文件,并写入数据
        """
        self.meta_info_path = self.folder_path+ '/draft_meta_info.json'
        self.content_path = self.folder_path + '/draft_content.json'
        # 创建文件夹
        os.makedirs(self.folder_path, exist_ok=True)
        # 创建 draft_meta_info.json
        with open(self.meta_info_path, 'w', encoding='utf-8') as meta_info_file:
            json.dump(self.draft_meta_template, meta_info_file, indent=4, ensure_ascii=False)

        with open(self.content_path, 'w', encoding='utf-8') as content_file:
            json.dump(self.draft_content_template, content_file, indent=4, ensure_ascii=False)
       